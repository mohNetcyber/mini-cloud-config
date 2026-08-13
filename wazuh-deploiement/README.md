# Déploiement Wazuh — Mini-cloud privé sécurisé

Fichiers de configuration et d'installation pour la partie **Wazuh** du projet
(responsable : El Mahdi), à transmettre à Mohamed pour exécution sur les VMs
réelles (VM4 pour le Manager, VM1/VM2/VM5 pour les agents).

Ces fichiers ont été préparés et vérifiés (syntaxe, cohérence avec
l'architecture) sur un Mac sans VM ; ils sont conçus pour être exécutés tels
quels sur les VMs Ubuntu Server 22.04 du binôme.

---

## Architecture de référence (extraite du document d'architecture du projet)

| VM | Rôle | IP | Composant Wazuh |
|---|---|---|---|
| VM1 — K3s Server | Control plane K3s + app de test | 192.168.100.10 | Agent |
| VM2 — K3s Worker | Nœud worker K3s | 192.168.100.11 | Agent |
| VM3 — Monitoring | Prometheus / Grafana | 192.168.100.12 | — |
| **VM4 — Wazuh Manager** | **Manager + Indexer + Dashboard** | **192.168.100.13** | **Manager** |
| VM5 — VM de test | Cible des scénarios d'incidents | 192.168.100.14 | Agent |

Réseau : NAT VMware (VMnet8), sous-réseau `192.168.100.0/24`.

**Point de vigilance :** ces IP diffèrent de celles utilisées dans le guide de
réalisation générique fourni par l'encadrante (qui suppose 3 VMs). Tous les
fichiers de ce dépôt utilisent exclusivement les IP du document d'architecture
du binôme (5 VMs). Vérifier cette cohérence avant toute exécution.

---

## Contenu

```
wazuh-deploiement/
├── README.md                                  (ce fichier)
├── manager/
│   ├── install-manager.sh                      → à exécuter sur VM4
│   ├── local_rules_additions.xml                → règles à ajouter sur VM4
│   └── docker-compose-local-test-README.md      → test local optionnel (Mac)
├── agents/
│   └── install-agent.sh                        → à exécuter sur VM1, VM2, VM5
└── config/
    └── ossec-agent-fim-snippet.xml              → config FIM pour les agents
```

---

## Procédure de déploiement (côté Mohamed, sur les vraies VMs)

### 1. Sur VM4 (192.168.100.13) — Wazuh Manager

```bash
chmod +x install-manager.sh
./install-manager.sh
```

Le script installe la stack complète (Manager + Indexer + Dashboard) via la
méthode officielle Wazuh 4.8, conforme au guide de réalisation (section 4.1).

Puis intégrer les règles personnalisées :
1. Ouvrir `/var/ossec/etc/rules/local_rules.xml` sur VM4
2. Copier le contenu de `local_rules_additions.xml` à l'intérieur
3. Redémarrer : `sudo systemctl restart wazuh-manager`

### 2. Sur VM1, VM2 et VM5 — Agents

**Rappel de dépendance (voir guide, "Principe de travail") :** sur VM1 et VM2,
attendre que K3s soit opérationnel (Phase 2) avant d'installer l'agent. Sur
VM5, aucune dépendance — peut être fait dès que le Manager (VM4) est prêt.

Sur chaque machine :
```bash
chmod +x install-agent.sh
./install-agent.sh
```

Le script détecte automatiquement l'IP de la machine et confirme son rôle
dans l'architecture. Il installe l'agent et l'enregistre auprès du Manager
(192.168.100.13).

Ensuite, appliquer la configuration FIM :
1. Ouvrir `/var/ossec/etc/ossec.conf` sur la machine
2. Remplacer le bloc `<syscheck>...</syscheck>` existant par le contenu de
   `config/ossec-agent-fim-snippet.xml`
3. Redémarrer : `sudo systemctl restart wazuh-agent`

### 3. Vérification finale (sur VM4)

```bash
sudo /var/ossec/bin/agent_control -l
```

Les 3 agents (VM1, VM2, VM5) doivent apparaître avec le statut **Active**.

---

## Validation attendue (checkpoint Phase 4 du guide)

- [ ] Le Wazuh Manager est accessible via `https://192.168.100.13`
- [ ] Les agents VM1, VM2 et VM5 apparaissent "Active" dans le Dashboard
- [ ] Une tentative de connexion SSH avec mauvais mot de passe génère une
      alerte visible en moins de 30 secondes
- [ ] Une modification de `/etc/passwd` ou `/etc/ssh/sshd_config` déclenche
      une alerte FIM (grâce aux règles personnalisées 100020/100021)

---

## Transmission des fichiers

Ce dossier peut être transmis à Mohamed soit par dépôt Git partagé, soit par
transfert direct (clé USB, partage réseau) — au choix du binôme.
