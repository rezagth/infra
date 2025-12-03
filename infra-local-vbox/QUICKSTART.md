# 🚀 Guide de Démarrage Rapide - Infrastructure Wazuh

Ce guide vous permet de déployer rapidement votre infrastructure Wazuh en quelques minutes.

## 📖 Étapes de Déploiement

### 1️⃣ Démarrer les VMs (5-10 minutes)

```powershell
# Dans le dossier infra-local-vbox
vagrant up
```

Cette commande crée et démarre :
- ✅ **wazuh-server** (192.168.56.10) - 4GB RAM, 2 CPUs
- ✅ **client01** (192.168.56.11) - 1GB RAM, 1 CPU
- ✅ **client02** (192.168.56.12) - 1GB RAM, 1 CPU

### 2️⃣ Déployer Wazuh (15-20 minutes)

```powershell
# Exécuter le playbook Ansible
ansible-playbook -i ansible/inventories/hosts.ini ansible/playbooks/site.yml
```

Le déploiement automatique :
1. ⚙️ Configure le système et applique le hardening
2. 📦 Installe Wazuh Server (Manager + Indexer + Dashboard)
3. 🔌 Installe les agents sur les clients
4. 🔐 Enregistre automatiquement les agents
5. ✅ Vérifie que tout fonctionne

### 3️⃣ Accéder au Dashboard Wazuh

**URL**: https://192.168.56.10

**Récupérer les credentials** :
```powershell
vagrant ssh wazuh-server -c "sudo cat /root/wazuh-install-credentials.txt"
```

Copiez le mot de passe affiché et connectez-vous avec :
- 👤 Utilisateur : `admin`
- 🔑 Mot de passe : [celui affiché]

## ✅ Vérifications Post-Déploiement

### Vérifier les agents connectés

```powershell
vagrant ssh wazuh-server -c "sudo /var/ossec/bin/agent_control -l"
```

Vous devriez voir client01 et client02 avec le statut **Active**.

### Tester la détection d'événements

```powershell
# Générer des événements SSH sur client01
vagrant ssh client01
ssh invalid-user@localhost  # Générera des alertes de sécurité
```

Allez dans le Dashboard → Security Events pour voir les alertes.

## 🛠️ Commandes Utiles

### Gérer les VMs

```powershell
vagrant status              # Voir l'état de toutes les VMs
vagrant halt                # Arrêter toutes les VMs
vagrant halt wazuh-server   # Arrêter seulement le serveur
vagrant reload client01     # Redémarrer client01
vagrant destroy -f          # Tout supprimer (attention !)
```

### Connexion SSH

```powershell
vagrant ssh wazuh-server    # Se connecter au serveur
vagrant ssh client01        # Se connecter au client 01
vagrant ssh client02        # Se connecter au client 02
```

### Vérifier les services

```powershell
# Sur le serveur
vagrant ssh wazuh-server -c "sudo systemctl status wazuh-manager wazuh-indexer wazuh-dashboard"

# Sur un agent
vagrant ssh client01 -c "sudo systemctl status wazuh-agent"
```

## 🔧 Configuration Rapide

### Ajouter un 3ème client

1. Modifier `Vagrantfile` - ajouter :
```ruby
config.vm.define "client03" do |client|
  client.vm.hostname = "client03"
  client.vm.network "private_network", ip: "192.168.56.13"
  client.vm.provider "virtualbox" do |vb|
    vb.name = "wazuh-client03"
    vb.memory = "1024"
    vb.cpus = 1
  end
end
```

2. Modifier `ansible/inventories/hosts.ini` :
```ini
[wazuh_agents]
client01 ansible_host=192.168.56.11
client02 ansible_host=192.168.56.12
client03 ansible_host=192.168.56.13
```

3. Déployer :
```powershell
vagrant up client03
ansible-playbook -i ansible/inventories/hosts.ini ansible/playbooks/site.yml --limit client03
```

## 📊 Monitoring dans le Dashboard

### Navigation principale

- **Security Events** : Voir toutes les alertes de sécurité
- **Integrity Monitoring** : Surveiller les modifications de fichiers
- **Vulnerability Detection** : Voir les vulnérabilités détectées
- **Security Configuration** : Résultats des audits de conformité
- **Agents** : État et gestion des agents

### Filtres utiles

Dans Security Events, essayez :
- `agent.name: client01` - Événements de client01 uniquement
- `rule.level: >= 10` - Alertes critiques seulement
- `rule.groups: authentication_failed` - Échecs d'authentification

## 🐛 Problèmes Courants

### Agent non connecté

```powershell
# Redémarrer l'agent
vagrant ssh client01 -c "sudo systemctl restart wazuh-agent"

# Vérifier les logs
vagrant ssh client01 -c "sudo tail -50 /var/ossec/logs/ossec.log"
```

### Dashboard inaccessible

```powershell
# Vérifier le service
vagrant ssh wazuh-server -c "sudo systemctl status wazuh-dashboard"

# Redémarrer si nécessaire
vagrant ssh wazuh-server -c "sudo systemctl restart wazuh-dashboard"
```

### Vagrant up échoue

```powershell
# Vérifier VirtualBox
VBoxManage list vms

# Nettoyer et recommencer
vagrant destroy -f
vagrant up
```

## 📚 Prochaines Étapes

1. 🎯 **Explorer le Dashboard** : Familiarisez-vous avec l'interface
2. 🔍 **Générer des alertes de test** : Testez la détection
3. ⚙️ **Personnaliser les règles** : Adaptez Wazuh à vos besoins
4. 📈 **Créer des tableaux de bord** : Visualisez vos métriques
5. 📧 **Configurer les alertes email** : Recevez des notifications

## 🆘 Besoin d'aide ?

- 📖 Consultez le [README.md](README.md) pour plus de détails
- 🌐 [Documentation Wazuh](https://documentation.wazuh.com/)
- 💬 [Forum Wazuh](https://groups.google.com/g/wazuh)
- 🐙 [GitHub Wazuh](https://github.com/wazuh/wazuh)

---

**Bon monitoring !** 🎉
