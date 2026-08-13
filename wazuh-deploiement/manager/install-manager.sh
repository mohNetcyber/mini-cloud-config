#!/bin/bash
# ============================================================================
# install-manager.sh
# Installation de la stack Wazuh complète (Manager + Indexer + Dashboard)
#
# Cible : VM4 - Wazuh Manager
# IP prévue (architecture du projet) : 192.168.100.13
# OS attendu : Ubuntu Server 22.04 LTS
# Ressources attendues : 4 vCPU / 8 Go RAM / 60 Go disque
#
# A exécuter en tant qu'utilisateur avec droits sudo, sur VM4 uniquement.
# ============================================================================

set -e

EXPECTED_IP="192.168.100.13"
CURRENT_IP=$(hostname -I | awk '{print $1}')

echo "=============================================="
echo " Installation Wazuh Manager - VM4"
echo "=============================================="
echo "IP attendue    : ${EXPECTED_IP}"
echo "IP détectée    : ${CURRENT_IP}"
echo ""

if [ "$CURRENT_IP" != "$EXPECTED_IP" ]; then
    echo "ATTENTION : l'IP de cette machine (${CURRENT_IP}) ne correspond pas"
    echo "à l'IP prévue pour VM4 (${EXPECTED_IP}) dans le document d'architecture."
    echo "Vérifiez la configuration netplan avant de continuer (Phase 1.5 du guide)."
    read -p "Continuer quand même ? (o/N) " confirm
    if [ "$confirm" != "o" ] && [ "$confirm" != "O" ]; then
        echo "Installation annulée."
        exit 1
    fi
fi

echo ""
echo "--- Téléchargement du script d'installation officiel Wazuh 4.8 ---"
curl -sO https://packages.wazuh.com/4.8/wazuh-install.sh

echo ""
echo "--- Lancement de l'installation complète (Manager + Indexer + Dashboard) ---"
echo "Cette étape peut prendre 10 à 20 minutes selon les ressources de la VM."
sudo bash wazuh-install.sh -a

echo ""
echo "=============================================="
echo " Installation terminée"
echo "=============================================="
echo "IMPORTANT : les mots de passe générés par le script ci-dessus"
echo "doivent être copiés IMMEDIATEMENT dans le journal de bord (El Mahdi)."
echo ""
echo "Accès au Wazuh Dashboard : https://${EXPECTED_IP}"
echo "Login : admin"
echo "Mot de passe : voir sortie ci-dessus (ou fichier wazuh-install-files.tar)"
echo ""
echo "Prochaine étape : copier local_rules_additions.xml dans"
echo "/var/ossec/etc/rules/local_rules.xml puis redémarrer le manager :"
echo "  sudo systemctl restart wazuh-manager"
