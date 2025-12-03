# Infrastructure Wazuh - VirtualBox

Infrastructure automatisée de sécurité utilisant **Wazuh** pour le monitoring et la détection de menaces, déployée sur VirtualBox avec Vagrant et Ansible.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    VirtualBox Host                       │
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Wazuh Server    │         │    Client 01     │     │
│  │  192.168.56.10   │◄────────│  192.168.56.11   │     │
│  │                  │         │  (Wazuh Agent)   │     │
│  │  • Manager       │         └──────────────────┘     │
│  │  • Indexer       │                                   │
│  │  • Dashboard     │         ┌──────────────────┐     │
│  └──────────────────┘◄────────│    Client 02     │     │
│         ↓                      │  192.168.56.12   │     │
│    Dashboard HTTPS             │  (Wazuh Agent)   │     │
│         ↓                      └──────────────────┘     │
│  https://192.168.56.10                                  │
└─────────────────────────────────────────────────────────┘
```

### Composants

- **Wazuh Server** (4GB RAM, 2 CPUs)
  - Wazuh Manager : Serveur central SIEM
  - Wazuh Indexer : Moteur de recherche (OpenSearch)
  - Wazuh Dashboard : Interface web de visualisation
  
- **Clients** (1GB RAM, 1 CPU chacun)
  - Wazuh Agent : Collecte et envoie les événements
  - Monitoring : Logs, FIM, SCA, Rootcheck

## 📋 Prérequis

- **VirtualBox** 6.0+
- **Vagrant** 2.2+
- **Ansible** 2.9+
- **Ressources système** : Minimum 8GB RAM disponible sur l'hôte
- **Python** 3.x

## 🚀 Démarrage Rapide

### 1. Démarrer les VMs

```bash
# Démarrer toutes les VMs
vagrant up

# Ou démarrer individuellement
vagrant up wazuh-server
vagrant up client01
vagrant up client02
```

### 2. Déployer Wazuh avec Ansible

```bash
# Déploiement complet automatique
ansible-playbook -i ansible/inventories/hosts.ini ansible/playbooks/site.yml
```

Le playbook exécute automatiquement :
1. ✅ Configuration de base + hardening (tous les hôtes)
2. ✅ Installation serveur Wazuh (manager + indexer + dashboard)
3. ✅ Installation agents Wazuh sur les clients
4. ✅ Enregistrement automatique des agents
5. ✅ Vérification du déploiement

### 3. Accéder au Dashboard

Ouvrez votre navigateur : **https://192.168.56.10**

**Credentials par défaut** :
- Utilisateur : `admin`
- Mot de passe : Voir `/root/wazuh-install-credentials.txt` sur le serveur

```bash
# Récupérer le mot de passe
vagrant ssh wazuh-server -c "sudo cat /root/wazuh-install-credentials.txt"
```

## 🔧 Configuration

### Structure du Projet

```
infra-local-vbox/
├── Vagrantfile                    # Configuration VMs VirtualBox
├── ansible/
│   ├── ansible.cfg                # Configuration Ansible
│   ├── inventories/
│   │   └── hosts.ini              # Inventaire des hôtes
│   ├── group_vars/                # Variables par groupe
│   │   ├── all.yml                # Variables globales
│   │   ├── wazuh_servers.yml      # Variables serveur
│   │   └── wazuh_agents.yml       # Variables agents
│   ├── playbooks/
│   │   └── site.yml               # Playbook principal
│   └── roles/
│       ├── hardening/             # Durcissement système
│       ├── wazuh-server/          # Installation serveur Wazuh
│       └── wazuh-agent/           # Installation agent Wazuh
├── pipelines/
│   └── github-actions.yml         # CI/CD (optionnel)
└── scripts/
    └── gen_inventory_from_vagrant.py
```

### Personnalisation

#### Changer le nombre de clients

Éditez `Vagrantfile` pour ajouter d'autres clients :

```ruby
config.vm.define "client03" do |client|
  client.vm.hostname = "client03"
  client.vm.network "private_network", ip: "192.168.56.13"
  # ...
end
```

Puis ajoutez dans `ansible/inventories/hosts.ini` :

```ini
[wazuh_agents]
client01 ansible_host=192.168.56.11
client02 ansible_host=192.168.56.12
client03 ansible_host=192.168.56.13
```

#### Modifier les modules Wazuh

Éditez `ansible/group_vars/wazuh_agents.yml` :

```yaml
wazuh_agent_config:
  syscheck:
    enabled: true
    directories:
      - /etc
      - /usr/bin
      - /votre/dossier/custom
```

## 📊 Ports Utilisés

| Service | Port | Protocole | Description |
|---------|------|-----------|-------------|
| Wazuh Agent Connection | 1514 | TCP | Communication agents → manager |
| Agent Enrollment | 1515 | TCP | Enregistrement nouveaux agents |
| Wazuh API | 55000 | TCP/HTTPS | API REST Wazuh |
| Wazuh Indexer | 9200 | TCP/HTTP | OpenSearch (interne) |
| Wazuh Dashboard | 443 | TCP/HTTPS | Interface web |

## 🔍 Vérification et Monitoring

### Vérifier les services Wazuh

```bash
# Sur le serveur
vagrant ssh wazuh-server

# Vérifier les services
sudo systemctl status wazuh-manager
sudo systemctl status wazuh-indexer
sudo systemctl status wazuh-dashboard
```

### Lister les agents connectés

```bash
vagrant ssh wazuh-server -c "sudo /var/ossec/bin/agent_control -l"
```

### Vérifier les logs

```bash
# Logs du manager
vagrant ssh wazuh-server -c "sudo tail -f /var/ossec/logs/ossec.log"

# Logs d'un agent
vagrant ssh client01 -c "sudo tail -f /var/ossec/logs/ossec.log"
```

### Tester la détection

Générez des événements sur un client :

```bash
vagrant ssh client01

# Tentative de connexion SSH (génère des alertes)
ssh invalid-user@localhost

# Modifier un fichier surveillé
sudo touch /etc/test-fim-wazuh
```

Vérifiez les alertes dans le Dashboard Wazuh.

## 🛠️ Commandes Utiles

### Gestion des VMs

```bash
# Voir l'état des VMs
vagrant status

# Arrêter toutes les VMs
vagrant halt

# Redémarrer une VM
vagrant reload wazuh-server

# Détruire et recréer
vagrant destroy -f && vagrant up
```

### Gestion Ansible

```bash
# Tester la connectivité
ansible all -i ansible/inventories/hosts.ini -m ping

# Exécuter uniquement sur les serveurs
ansible-playbook -i ansible/inventories/hosts.ini ansible/playbooks/site.yml --limit wazuh_servers

# Mode verbose
ansible-playbook -i ansible/inventories/hosts.ini ansible/playbooks/site.yml -vvv
```

### Wazuh Manager

```bash
# Lister tous les agents
/var/ossec/bin/agent_control -l

# Voir les détails d'un agent
/var/ossec/bin/agent_control -i <agent-id>

# Supprimer un agent
/var/ossec/bin/manage_agents -r <agent-id>

# Redémarrer le manager
systemctl restart wazuh-manager
```

## 🐛 Dépannage

### Agent non connecté

```bash
# Sur l'agent
sudo systemctl status wazuh-agent
sudo systemctl restart wazuh-agent
sudo cat /var/ossec/logs/ossec.log

# Vérifier la connectivité
telnet 192.168.56.10 1514
```

### Dashboard inaccessible

```bash
# Sur le serveur
sudo systemctl status wazuh-dashboard
sudo systemctl restart wazuh-dashboard

# Vérifier les certificats
ls -la /etc/wazuh-indexer/certs/
```

### Problèmes de mémoire

Si le serveur manque de mémoire, augmentez dans `Vagrantfile` :

```ruby
vb.memory = "6144"  # 6GB au lieu de 4GB
```

## 📚 Ressources

- [Documentation Wazuh](https://documentation.wazuh.com/)
- [Wazuh GitHub](https://github.com/wazuh/wazuh)
- [Règles Wazuh](https://documentation.wazuh.com/current/user-manual/ruleset/index.html)
- [Ansible Documentation](https://docs.ansible.com/)

## 📄 License

MIT

