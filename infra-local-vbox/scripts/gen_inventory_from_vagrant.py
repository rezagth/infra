#!/usr/bin/env python3
"""
Script de génération automatique de l'inventaire Ansible à partir de Vagrant.
Lit les informations SSH de Vagrant et génère le fichier hosts.ini.
"""

import subprocess
import json
import os
from pathlib import Path


def get_vagrant_ssh_config():
    """Récupère la configuration SSH de toutes les VMs Vagrant."""
    try:
        # Exécuter vagrant ssh-config
        result = subprocess.run(
            ['vagrant', 'ssh-config'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de 'vagrant ssh-config': {e}")
        return None
    except FileNotFoundError:
        print("Vagrant n'est pas installé ou n'est pas dans le PATH")
        return None


def parse_ssh_config(ssh_config):
    """Parse la sortie de vagrant ssh-config."""
    hosts = {}
    current_host = None
    
    for line in ssh_config.split('\n'):
        line = line.strip()
        
        if line.startswith('Host '):
            current_host = line.split()[1]
            hosts[current_host] = {}
        elif current_host and line:
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                hosts[current_host][key] = value
    
    return hosts


def generate_inventory(hosts):
    """Génère le contenu du fichier hosts.ini."""
    inventory_lines = [
        "# Inventaire généré automatiquement depuis Vagrant",
        "# Généré par: scripts/gen_inventory_from_vagrant.py",
        "",
        "[all:vars]",
        "ansible_user=vagrant",
        ""
    ]
    
    # Grouper les hôtes par type (server ou agent)
    servers = []
    agents = []
    
    for hostname, config in hosts.items():
        if 'server' in hostname:
            servers.append((hostname, config))
        elif 'agent' in hostname:
            agents.append((hostname, config))
    
    # Groupe servers
    if servers:
        inventory_lines.append("[servers]")
        for hostname, config in servers:
            host_line = f"{hostname} ansible_host={config.get('HostName', '127.0.0.1')} "
            host_line += f"ansible_port={config.get('Port', '2222')} "
            host_line += f"ansible_ssh_private_key_file={config.get('IdentityFile', '').strip('\"')}"
            inventory_lines.append(host_line)
        inventory_lines.append("")
    
    # Groupe agents
    if agents:
        inventory_lines.append("[agents]")
        for hostname, config in agents:
            host_line = f"{hostname} ansible_host={config.get('HostName', '127.0.0.1')} "
            host_line += f"ansible_port={config.get('Port', '2222')} "
            host_line += f"ansible_ssh_private_key_file={config.get('IdentityFile', '').strip('\"')}"
            inventory_lines.append(host_line)
        inventory_lines.append("")
    
    # Groupe all
    inventory_lines.extend([
        "[all:children]",
        "servers" if servers else "# servers",
        "agents" if agents else "# agents",
        ""
    ])
    
    return '\n'.join(inventory_lines)


def main():
    """Fonction principale."""
    # Déterminer les chemins
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    inventory_path = project_dir / 'ansible' / 'inventories' / 'hosts.ini'
    
    print("🔍 Récupération de la configuration SSH de Vagrant...")
    ssh_config = get_vagrant_ssh_config()
    
    if not ssh_config:
        print("❌ Impossible de récupérer la configuration Vagrant")
        print("💡 Assurez-vous que les VMs sont démarrées avec 'vagrant up'")
        return 1
    
    print("📝 Parsing de la configuration...")
    hosts = parse_ssh_config(ssh_config)
    
    if not hosts:
        print("❌ Aucun hôte trouvé dans la configuration Vagrant")
        return 1
    
    print(f"✅ {len(hosts)} hôte(s) trouvé(s): {', '.join(hosts.keys())}")
    
    print("📄 Génération de l'inventaire...")
    inventory_content = generate_inventory(hosts)
    
    # Créer le répertoire si nécessaire
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Écrire le fichier
    inventory_path.write_text(inventory_content, encoding='utf-8')
    
    print(f"✅ Inventaire généré avec succès: {inventory_path}")
    print("\n📋 Contenu de l'inventaire:")
    print("=" * 60)
    print(inventory_content)
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())
