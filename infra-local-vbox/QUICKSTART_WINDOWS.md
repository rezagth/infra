# 🚀 Démarrage Rapide - Infrastructure Wazuh avec Windows

Guide pour déployer Wazuh avec un serveur Linux et un client Windows Server 2022.

## 📋 Prérequis

### Sur Windows (Hôte)
- **VirtualBox** 6.0+
- **Vagrant** 2.2+
- **8GB RAM** minimum sur la machine hôte

### Sur WSL Ubuntu
- **Ansible** : `pip install ansible`
- **pywinrm** : `pip install pywinrm` ⚠️ **IMPORTANT pour Windows**
- **Python** 3.x

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Votre PC Windows                │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ Wazuh Server │    │   Windows    │  │
│  │ Ubuntu 22.04 │◄───│  Server 2022 │  │
│  │ 4GB RAM      │    │  2GB RAM     │  │
│  │ .56.10       │    │  .56.20      │  │
│  └──────────────┘    └──────────────┘  │
│         ▲                               │
│         │ Dashboard                     │
│       Vous                              │
└─────────────────────────────────────────┘
```

## 📝 Étapes de Déploiement

### 1️⃣ Détruire les anciennes VMs (si existantes)

**Dans PowerShell** :
```powershell
cd C:\Users\MAON\Documents\infra\infra-local-vbox
vagrant destroy -f
```

### 2️⃣ Démarrer les VMs

```powershell
# Démarrer le serveur Wazuh (Ubuntu)
vagrant up wazuh-server

# Démarrer le client Windows (1ère fois: télécharge ~6GB)
vagrant up windows-client
```

⏱️ **Temps estimé** :
- Serveur: 3-5 minutes
- Windows (1ère fois): 15-20 minutes (téléchargement box)
- Windows (fois suivantes): 5 minutes

### 3️⃣ Préparer WSL pour Ansible

**Dans WSL Ubuntu** :
```bash
# Installer pywinrm (OBLIGATOIRE pour Windows)
pip install pywinrm

# Copier les clés SSH pour le serveur
mkdir -p ~/.ssh/vagrant-keys
cp /mnt/c/Users/MAON/Documents/infra/infra-local-vbox/.vagrant/machines/wazuh-server/virtualbox/private_key ~/.ssh/vagrant-keys/wazuh-server
chmod 600 ~/.ssh/vagrant-keys/wazuh-server

# Synchroniser le code
cd ~/workspaces/infra/infra-local-vbox
git pull
```

### 4️⃣ Tester les connexions

```bash
# Tester SSH vers le serveur
ssh -i ~/.ssh/vagrant-keys/wazuh-server vagrant@192.168.56.10 "echo 'SSH OK'"

# Tester WinRM vers Windows (nécessite pywinrm)
cd ~/workspaces/infra/infra-local-vbox/ansible
ansible wazuh_agents_windows -i inventories/hosts_windows.ini -m win_ping
```

Si `win_ping` réussit, vous êtes prêt ! ✅

### 5️⃣ Installer Wazuh Server

```bash
cd ~/workspaces/infra/infra-local-vbox/ansible

# Installer uniquement le serveur Wazuh (15-20 min)
ansible-playbook -i inventories/hosts_windows.ini playbooks/site_windows.yml --limit wazuh_servers
```

**Pendant l'installation**, vous verrez :
- ✅ Hardening du système
- ✅ Installation Wazuh Indexer (5 min)
- ✅ Installation Wazuh Manager (3 min)
- ✅ Installation Wazuh Dashboard (3 min)
- ✅ Vérification des services

### 6️⃣ Installer l'Agent Windows

```bash
# Installer l'agent sur le client Windows (3-5 min)
ansible-playbook -i inventories/hosts_windows.ini playbooks/site_windows.yml --limit wazuh_agents_windows
```

### 7️⃣ Accéder au Dashboard

**Récupérer le mot de passe** :
```bash
ssh -i ~/.ssh/vagrant-keys/wazuh-server vagrant@192.168.56.10 "sudo cat /root/wazuh-install-credentials.txt"
```

**Ouvrir le Dashboard** : https://192.168.56.10

- ⚠️ Accepter le certificat auto-signé
- 👤 User: `admin`
- 🔑 Password: (celui affiché ci-dessus)

### 8️⃣ Vérifier que l'agent Windows est connecté

**Dans le Dashboard** :
- Allez dans **Agents** (menu gauche)
- Vous devriez voir `windows-client` avec statut **Active**

**En ligne de commande** :
```bash
ssh -i ~/.ssh/vagrant-keys/wazuh-server vagrant@192.168.56.10 "sudo /var/ossec/bin/agent_control -l"
```

## ✅ Tests et Vérifications

### Générer des événements Windows

**Se connecter au Windows** :
```powershell
# Depuis PowerShell Windows
vagrant rdp windows-client
# ou
vagrant ssh windows-client
```

**Générer des alertes** :
```powershell
# Dans Windows PowerShell
# Événement de sécurité
net user test_user P@ssw0rd /add
net user test_user /delete

# Vérifier le service Wazuh
Get-Service WazuhSvc
```

**Voir les alertes** : Dashboard → Security Events

## 🛠️ Commandes Utiles

### Gestion VMs (PowerShell)

```powershell
vagrant status                    # État des VMs
vagrant halt                      # Arrêter tout
vagrant up wazuh-server          # Démarrer serveur
vagrant reload windows-client    # Redémarrer Windows
vagrant destroy -f               # Tout supprimer
```

### Connexion aux VMs

```powershell
# SSH vers le serveur Wazuh
vagrant ssh wazuh-server

# RDP vers Windows (si GUI activée)
vagrant rdp windows-client

# PowerShell vers Windows
vagrant ssh windows-client
```

### Ansible (WSL)

```bash
# Tester connectivité
ansible all -i inventories/hosts_windows.ini -m ping

# Déployer seulement serveur
ansible-playbook -i inventories/hosts_windows.ini playbooks/site_windows.yml --limit wazuh_servers

# Déployer seulement Windows
ansible-playbook -i inventories/hosts_windows.ini playbooks/site_windows.yml --limit wazuh_agents_windows

# Mode verbose
ansible-playbook -i inventories/hosts_windows.ini playbooks/site_windows.yml -vvv
```

## 🐛 Résolution de Problèmes

### pywinrm manquant

```bash
# Erreur: "winrm or requests is not installed"
pip install pywinrm
```

### Agent Windows non connecté

```powershell
# Sur le Windows client
Get-Service WazuhSvc
Restart-Service WazuhSvc

# Vérifier les logs
Get-Content "C:\Program Files (x86)\ossec-agent\ossec.log" -Tail 50
```

### WinRM non accessible

```bash
# Tester WinRM
ansible wazuh_agents_windows -i inventories/hosts_windows.ini -m win_ping

# Si ça échoue, redémarrer la VM Windows
vagrant reload windows-client
```

### Ralentissements

Si Windows est lent :
- Augmenter la RAM dans Vagrantfile : `vb.memory = "3072"` (3GB)
- Fermer d'autres applications sur l'hôte

## 📊 Surveillance dans le Dashboard

### Sections importantes

- **Agents** : Statut de votre agent Windows
- **Security Events** : Alertes de sécurité Windows
- **File Integrity Monitoring** : Modifications de fichiers
- **Vulnerability Detection** : CVEs Windows détectées

### Filtres utiles

```
agent.name: "windows-client"
data.win.system.computer: "windows-client"
rule.groups: "windows"
```

## 🎯 Prochaines Étapes

1. ✅ Explorer les événements Windows dans le Dashboard
2. 🔧 Personnaliser les règles de détection
3. 📧 Configurer les notifications (email, Slack)
4. 📈 Créer des tableaux de bord personnalisés

---

**Besoin d'aide ?** Consultez le [README.md](../README.md) complet !
