# Infrastructure Locale VirtualBox

Infrastructure de test locale utilisant Vagrant et Ansible pour le provisioning et la configuration.

## Structure du Projet

```
infra-local-vbox/
├── Vagrantfile              # Configuration des VMs VirtualBox
├── ansible/
│   ├── ansible.cfg          # Configuration Ansible
│   ├── inventories/
│   │   └── hosts.ini        # Inventaire généré automatiquement
│   ├── playbooks/
│   │   └── site.yml         # Playbook principal
│   └── roles/
│       ├── hardening/       # Rôle de durcissement système
│       ├── edr/             # Rôle EDR (Endpoint Detection & Response)
│       └── wazuh/           # Rôle Wazuh SIEM
├── pipelines/
│   └── github-actions.yml   # CI/CD (optionnel)
└── scripts/
    └── gen_inventory_from_vagrant.py  # Génération automatique de l'inventaire
```

## Prérequis

- VirtualBox
- Vagrant
- Ansible
- Python 3.x

## Utilisation

1. **Démarrer l'environnement**
   ```bash
   vagrant up
   ```

2. **Générer l'inventaire Ansible**
   ```bash
   python scripts/gen_inventory_from_vagrant.py
   ```

3. **Exécuter le provisioning Ansible**
   ```bash
   ansible-playbook -i ansible/inventories/hosts.ini ansible/playbooks/site.yml
   ```

## Rôles Ansible

- **hardening**: Durcissement de la sécurité système
- **edr**: Installation et configuration EDR
- **wazuh**: Déploiement de Wazuh pour le monitoring et la détection

## License

MIT
