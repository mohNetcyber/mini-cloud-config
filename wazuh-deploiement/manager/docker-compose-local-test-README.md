# docker-compose-local-test.yml
#
# USAGE : test local UNIQUEMENT, sur le Mac d'El Mahdi (macOS + Docker Desktop),
# pour valider visuellement le Wazuh Dashboard et la syntaxe des fichiers de
# configuration AVANT de les transmettre à Mohamed pour l'installation réelle
# sur VM4 (192.168.100.13).
#
# Ce fichier NE remplace PAS l'installation réelle décrite dans
# manager/install-manager.sh, qui reste la méthode officielle à utiliser
# sur VM4 (conforme au guide de réalisation, section 4.1).
#
# Prérequis : Docker Desktop, au moins 4 Go de RAM alloués à Docker.
#
# Utilisation :
#   git clone https://github.com/wazuh/wazuh-docker.git -b v4.8.0
#   cd wazuh-docker/single-node
#   docker compose up -d
#   # Accès : https://localhost (login admin / mot de passe par défaut du dépôt officiel)
#
# Le dépôt officiel wazuh-docker contient déjà son propre docker-compose.yml
# préconfiguré : il n'est pas nécessaire d'en réécrire un depuis zéro.
# Ce fichier sert uniquement de pense-bête pour la procédure ci-dessus.
