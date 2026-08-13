#!/bin/bash
# ============================================================================
# install-agent.sh
# Installation et enregistrement d'un agent Wazuh
#
# A exécuter sur CHAQUE machine à surveiller :
#   - VM1 - K3s Server      (192.168.100.10)
#   - VM2 - K3s Worker      (192.168.100.11)
#   - VM5 - VM de test      (192.168.100.14)
#
# Dépendance (voir guide, "Principe de travail") :
#   - Sur VM1 et VM2 : cette étape attend que K3s soit opérationnel (Phase 2,
#     responsable Mohamed) - c'est la seule vraie dépendance entre les deux
#     parties du binôme.
#   - Sur VM5 : aucune dépendance, peut être fait dès que le Manager (VM4)
#     est installé.
#
# Le Wazuh Manager (VM4) doit être installé et démarré AVANT d'exécuter
# ce script sur les machines cibles.
# ============================================================================

set -e

WAZUH_MANAGER_IP="192.168.100.13"   # VM4 - Wazuh Manager (voir architecture)
WAZUH_VERSION="4.8.0-1"

CURRENT_IP=$(hostname -I | awk '{print $1}')

echo "=============================================="
echo " Installation Agent Wazuh"
echo "=============================================="
echo "IP de cette machine     : ${CURRENT_IP}"
echo "IP du Wazuh Manager (VM4): ${WAZUH_MANAGER_IP}"
echo ""

case "$CURRENT_IP" in
    192.168.100.10) ROLE="VM1 - K3s Server" ;;
    192.168.100.11) ROLE="VM2 - K3s Worker" ;;
    192.168.100.14) ROLE="VM5 - VM de test" ;;
    *) ROLE="Machine non identifiée dans l'architecture du projet" ;;
esac
echo "Rôle détecté : ${ROLE}"
echo ""

echo "--- Test de connectivité vers le Wazuh Manager ---"
if ! ping -c 2 "${WAZUH_MANAGER_IP}" > /dev/null 2>&1; then
    echo "ERREUR : impossible de joindre ${WAZUH_MANAGER_IP} (VM4)."
    echo "Vérifiez que VM4 est démarrée et que le réseau NAT VMware (VMnet8)"
    echo "est correctement configuré avant de continuer."
    exit 1
fi
echo "OK - Manager joignable."
echo ""

echo "--- Téléchargement du paquet agent Wazuh ${WAZUH_VERSION} ---"
curl -so wazuh-agent.deb "https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_${WAZUH_VERSION}_amd64.deb"

echo ""
echo "--- Installation avec enregistrement automatique vers ${WAZUH_MANAGER_IP} ---"
sudo WAZUH_MANAGER="${WAZUH_MANAGER_IP}" dpkg -i ./wazuh-agent.deb

echo ""
echo "--- Application de la configuration FIM (syscheck) ---"
CONFIG_FILE="/var/ossec/etc/ossec.conf"
if [ -f "$CONFIG_FILE" ]; then
    sudo cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.$(date +%Y%m%d%H%M%S)"
    echo "Sauvegarde de la config existante effectuée (.bak)."
    echo "Insérez maintenant manuellement le contenu de"
    echo "config/ossec-agent-fim-snippet.xml dans ${CONFIG_FILE}"
    echo "(voir instructions dans le README)."
else
    echo "ATTENTION : ${CONFIG_FILE} introuvable, vérifiez l'installation."
fi

echo ""
echo "--- Démarrage du service agent ---"
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
sudo systemctl status wazuh-agent --no-pager

echo ""
echo "=============================================="
echo " Installation agent terminée sur : ${ROLE}"
echo "=============================================="
echo "Vérification côté Manager (à exécuter sur VM4) :"
echo "  sudo /var/ossec/bin/agent_control -l"
echo ""
echo "L'agent doit apparaître avec le statut 'Active'."
