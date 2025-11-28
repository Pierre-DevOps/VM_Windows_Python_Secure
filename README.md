\# Déploiement sécurisé de VM Windows Server sur Azure



Script Python pour déployer automatiquement une VM Windows Server 2022 sur Azure avec sécurité renforcée.



Projet de formation DevOps - Bachelor Administrateur Système DevOps (RNCP36061)



\## Objectifs



\- Automatiser le déploiement d'infrastructure cloud

\- Appliquer les principes DevSecOps

\- Infrastructure as Code avec Python

\- Gestion sécurisée des secrets



\## Ce qui est déployé



\- Resource Group

\- Virtual Network + Subnet

\- Network Security Group (NSG restrictif)

\- IP publique

\- Interface réseau

\- VM Windows Server 2022



\## Sécurité



\### NSG restrictif

\- Accès RDP limité à une seule IP source

\- Règle de blocage par défaut (Deny All)



\### Secrets protégés

\- Fichier `.env` pour les credentials (non versionné)

\- Aucun secret dans le code

\- Configuration séparée



\## Installation rapide



```bash

\# 1. Cloner

git clone https://github.com/Pierre-DevOps/VM\_Windows\_Python\_Secure.git

cd VM\_Windows\_Python\_Secure



\# 2. Environnement virtuel

python -m venv venv

.\\venv\\Scripts\\Activate.ps1



\# 3. Dépendances

pip install -r requirements.txt



\# 4. Azure

az login

```



\## Configuration



Créer un fichier `.env` :



```env

AZURE\_SUBSCRIPTION\_ID=votre-subscription-id

AZURE\_VM\_ADMIN\_USERNAME=votreusername

AZURE\_VM\_ADMIN\_PASSWORD=VotreMotDePasseSecurise123!

ALLOWED\_SOURCE\_IP=votre.ip.publique/32

```



⚠️ \*\*Ne JAMAIS commiter le fichier `.env` sur Git !\*\*



\## Utilisation



```bash

python deploy\_vm\_secure.py

```



Durée : ~5 minutes



\## Connexion RDP



```bash

mstsc /v:IP\_PUBLIQUE

```



\## Technologies



\- Python 3.8+

\- Azure SDK (compute, network, resource)

\- Azure CLI

\- YAML + dotenv



\## Spécifications



\- \*\*OS\*\* : Windows Server 2022

\- \*\*Taille\*\* : Standard\_B1s

\- \*\*Région\*\* : Switzerland North

\- \*\*VNet\*\* : 10.0.0.0/16



\## Compétences démontrées



\- Infrastructure as Code

\- Programmation Python

\- Azure SDK

\- Sécurité réseau (NSG)

\- DevSecOps



\## Améliorations possibles



\- Azure Key Vault

\- Disk Encryption

\- Managed Identity

\- Azure Monitor

\- Pipeline CI/CD



\## Contexte



Formation : Bachelor Administrateur Système DevOps (RNCP36061)  

Certifications : Azure AZ-900 ✅ | AZ-104 (en cours)



Projet pour le référentiel AT1 : "Automatiser le déploiement d'une infrastructure"



\## Auteur



Pierre - Étudiant DevOps  

GitHub : \[@Pierre-DevOps](https://github.com/Pierre-DevOps)

