#!/usr/bin/env python3
"""
Deploiement securise d'une VM Windows Server sur Azure
Projet DevSecOps - Pierre
"""

import os
import sys
import yaml
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network.models import (
    NetworkSecurityGroup, SecurityRule, VirtualNetwork, 
    Subnet, PublicIPAddress, NetworkInterface, 
    NetworkInterfaceIPConfiguration
)
from azure.mgmt.compute.models import (
    VirtualMachine, HardwareProfile, StorageProfile,
    OSProfile, NetworkProfile, OSDisk, ImageReference,
    ManagedDiskParameters, NetworkInterfaceReference
)

print("Deploiement securise de VM Windows Server sur Azure")
print("=" * 70)

# ETAPE 1 : Charger la configuration
print("\n[1/8] Chargement de la configuration...")
load_dotenv()

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Recuperation des secrets depuis .env
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
ADMIN_USERNAME = os.getenv('AZURE_VM_ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('AZURE_VM_ADMIN_PASSWORD')
ALLOWED_IP = os.getenv('ALLOWED_SOURCE_IP')

# Validation des variables
if not all([SUBSCRIPTION_ID, ADMIN_USERNAME, ADMIN_PASSWORD, ALLOWED_IP]):
    print("ERREUR : Variables manquantes dans le fichier .env")
    sys.exit(1)

print("Configuration chargee avec succes")
print(f"   - Subscription: {SUBSCRIPTION_ID[:8]}...")
print(f"   - Location: {config['location']}")
print(f"   - IP autorisee: {ALLOWED_IP}")

# ETAPE 2 : Connexion aux services Azure
print("\n[2/8] Connexion aux services Azure...")
credential = DefaultAzureCredential()

resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
network_client = NetworkManagementClient(credential, SUBSCRIPTION_ID)
compute_client = ComputeManagementClient(credential, SUBSCRIPTION_ID)

print("Connexion etablie avec succes")

# ETAPE 3 : Creation du groupe de ressources
print("\n[3/8] Creation du groupe de ressources...")
rg_name = config['resource_group']['name']
location = config['location']

resource_client.resource_groups.create_or_update(
    rg_name,
    {'location': location}
)
print(f"Groupe de ressources cree : {rg_name}")

# ETAPE 4 : Creation du Network Security Group (NSG) SECURISE
print("\n[4/8] Creation du NSG securise...")
nsg_name = config['network']['nsg_name']

# Regle RDP RESTRICTIVE - Seulement ton IP !
rdp_rule = SecurityRule(
    name='Allow-RDP-MyIP',
    protocol='Tcp',
    source_port_range='*',
    destination_port_range='3389',
    source_address_prefix=ALLOWED_IP,  # TON IP UNIQUEMENT
    destination_address_prefix='*',
    access='Allow',
    priority=1000,
    direction='Inbound'
)

# Regle pour BLOQUER tout le reste
deny_all_rule = SecurityRule(
    name='Deny-All-Inbound',
    protocol='*',
    source_port_range='*',
    destination_port_range='*',
    source_address_prefix='*',
    destination_address_prefix='*',
    access='Deny',
    priority=4096,
    direction='Inbound'
)

nsg_params = NetworkSecurityGroup(
    location=location,
    security_rules=[rdp_rule, deny_all_rule]
)

nsg = network_client.network_security_groups.begin_create_or_update(
    rg_name,
    nsg_name,
    nsg_params
).result()

print(f"NSG cree avec regles restrictives")
print(f"   - RDP autorise UNIQUEMENT depuis: {ALLOWED_IP}")
print(f"   - Tout le reste est BLOQUE")# ETAPE 5 : Creation du Virtual Network et Subnet
print("\n[5/8] Creation du VNet et Subnet...")
vnet_name = config['network']['vnet_name']
subnet_name = config['network']['subnet_name']

subnet_params = Subnet(
    name=subnet_name,
    address_prefix=config['network']['subnet_prefix'],
    network_security_group={'id': nsg.id}
)

vnet_params = VirtualNetwork(
    location=location,
    address_space={'address_prefixes': [config['network']['vnet_prefix']]},
    subnets=[subnet_params]
)

vnet = network_client.virtual_networks.begin_create_or_update(
    rg_name,
    vnet_name,
    vnet_params
).result()

print(f"VNet cree : {vnet_name}")

# ETAPE 6 : Creation de l'IP publique
print("\n[6/8] Creation de l'IP publique...")
ip_name = f"pip-{config['vm']['name']}"

ip_params = PublicIPAddress(
    location=location,
    sku={'name': 'Standard'},
    public_ip_allocation_method='Static'
)

public_ip = network_client.public_ip_addresses.begin_create_or_update(
    rg_name,
    ip_name,
    ip_params
).result()

print(f"IP publique creee : {ip_name}")

# ETAPE 7 : Creation de l'interface reseau
print("\n[7/8] Creation de l'interface reseau...")
nic_name = f"nic-{config['vm']['name']}"

ip_config = NetworkInterfaceIPConfiguration(
    name='ipconfig1',
    subnet={'id': vnet.subnets[0].id},
    public_ip_address={'id': public_ip.id}
)

nic_params = NetworkInterface(
    location=location,
    ip_configurations=[ip_config]
)

nic = network_client.network_interfaces.begin_create_or_update(
    rg_name,
    nic_name,
    nic_params
).result()

print(f"Interface reseau creee : {nic_name}")

# ETAPE 8 : Creation de la VM Windows Server 2022
print("\n[8/8] Creation de la VM (cela peut prendre 3-5 minutes)...")
vm_name = config['vm']['name']

vm_params = VirtualMachine(
    location=location,
    hardware_profile=HardwareProfile(
        vm_size=config['vm']['size']
    ),
    storage_profile=StorageProfile(
        image_reference=ImageReference(
            publisher=config['vm']['image']['publisher'],
            offer=config['vm']['image']['offer'],
            sku=config['vm']['image']['sku'],
            version=config['vm']['image']['version']
        ),
        os_disk=OSDisk(
            name=f"osdisk-{vm_name}",
            caching='ReadWrite',
            create_option='FromImage',
            managed_disk=ManagedDiskParameters(
                storage_account_type='Premium_LRS'
            )
        )
    ),
    os_profile=OSProfile(
        computer_name=vm_name,
        admin_username=ADMIN_USERNAME,
        admin_password=ADMIN_PASSWORD,
        windows_configuration={
            'provision_vm_agent': True,
            'enable_automatic_updates': True
        }
    ),
    network_profile=NetworkProfile(
        network_interfaces=[
            NetworkInterfaceReference(id=nic.id, primary=True)
        ]
    )
)

vm = compute_client.virtual_machines.begin_create_or_update(
    rg_name,
    vm_name,
    vm_params
).result()

print(f"VM creee avec succes : {vm_name}")

# Recuperation de l'IP publique
public_ip_address = network_client.public_ip_addresses.get(
    rg_name,
    ip_name
)

print("\n" + "=" * 70)
print("DEPLOIEMENT TERMINE AVEC SUCCES")
print("=" * 70)
print(f"Nom de la VM    : {vm_name}")
print(f"IP publique     : {public_ip_address.ip_address}")
print(f"Utilisateur     : {ADMIN_USERNAME}")
print(f"Localisation    : {location}")
print(f"\nConnexion RDP   : mstsc /v:{public_ip_address.ip_address}")
print("=" * 70)

