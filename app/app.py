from flask import Flask, Response, request, render_template_string
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

APP_NAME = 'app-test'

# Compteur defini manuellement, avec le nom et les labels exacts
# attendus par la requete PromQL du dashboard :
#   sum(rate(http_requests_total{status=~"5.."}[5m])) by (app)
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Nombre total de requetes HTTP recues',
    ['method', 'status', 'app']
)

PAGE_STYLE = """
<style>
    :root {
        --bg: #0b1020;
        --panel: rgba(16, 24, 40, 0.9);
        --panel-strong: #121b2b;
        --primary: #58a6ff;
        --primary-strong: #2f81f7;
        --success: #2dd4bf;
        --danger: #f87171;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --border: rgba(148, 163, 184, 0.18);
        --shadow: 0 18px 40px rgba(15, 23, 42, 0.45);
    }

    * { box-sizing: border-box; }

    body {
        margin: 0;
        min-height: 100vh;
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(135deg, #0b1020 0%, #111827 45%, #172033 100%);
        color: var(--text);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px 18px;
    }

    .container {
        width: min(920px, 100%);
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 24px;
        box-shadow: var(--shadow);
        padding: 32px 28px;
        backdrop-filter: blur(10px);
    }

    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 24px;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(88, 166, 255, 0.12);
        color: var(--primary);
        border: 1px solid rgba(88, 166, 255, 0.35);
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 999px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }

    .status-pill.ok {
        background: rgba(45, 212, 191, 0.12);
        color: var(--success);
        border: 1px solid rgba(45, 212, 191, 0.35);
    }

    .status-pill.error {
        background: rgba(248, 113, 113, 0.12);
        color: var(--danger);
        border: 1px solid rgba(248, 113, 113, 0.35);
    }

    h1 {
        margin: 0 0 10px;
        font-size: clamp(2rem, 3vw, 3rem);
        line-height: 1.15;
    }

    .subtitle {
        margin: 0;
        color: var(--muted);
        font-size: 1.04rem;
        line-height: 1.6;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 18px;
        margin-top: 26px;
    }

    .card {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 20px;
    }

    .card h2 {
        margin: 0 0 12px;
        font-size: 1rem;
        color: var(--muted);
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .card strong {
        display: block;
        font-size: 1.8rem;
        line-height: 1.1;
        margin-bottom: 6px;
    }

    .card p {
        margin: 0;
        color: var(--muted);
        line-height: 1.5;
    }

    .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 28px;
    }

    .button {
        display: inline-block;
        padding: 12px 18px;
        border-radius: 12px;
        color: white;
        text-decoration: none;
        font-weight: 700;
        transition: transform 0.15s ease, opacity 0.15s ease;
    }

    .button:hover {
        transform: translateY(-1px);
        opacity: 0.96;
    }

    .button.primary {
        background: linear-gradient(135deg, var(--primary), var(--primary-strong));
    }

    .button.secondary {
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid var(--border);
    }

    .button.danger {
        background: linear-gradient(135deg, #ef4444, #f87171);
    }

    .footer-note {
        margin-top: 28px;
        color: var(--muted);
        font-size: 0.9rem;
    }

    @media (max-width: 640px) {
        .container {
            padding: 22px 18px;
        }
        .header {
            align-items: flex-start;
        }
    }
</style>
"""

HOME_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ app_name }} - Mini Cloud</title>
    {{ style | safe }}
</head>
<body>
    <main class="container">
        <div class="header">
            <div>
                <span class="badge">Service actif</span>
                <h1>{{ app_name }}</h1>
            </div>
            <span class="status-pill ok">● En ligne</span>
        </div>

        <p class="subtitle">
            Application de test déployée dans le mini-cloud K3s. Elle surveille sa santé,
            simule des erreurs pour les tests de supervision et expose des métriques Prometheus.
        </p>

        <section class="grid">
            <article class="card">
                <h2>Route</h2>
                <strong>/health</strong>
                <p>Ce point de contrôle est utilisé par les probes Kubernetes pour vérifier l’état du service.</p>
            </article>
            <article class="card">
                <h2>Métriques</h2>
                <strong>/metrics</strong>
                <p>L’application expose des métriques Prometheus via la bibliothèque python prometheus_client.</p>
            </article>
            <article class="card">
                <h2>Supervision</h2>
                <strong>Grafana + Prometheus</strong>
                <p>Le dépôt contient un datasource Prometheus et un dashboard Grafana pour exploiter ces métriques.</p>
            </article>
        </section>

        <div class="actions">
            <a class="button primary" href="/health">Vérifier la santé</a>
            <a class="button secondary" href="/metrics">Voir les métriques</a>
            <a class="button danger" href="/error">Simuler une erreur</a>
        </div>

        <div class="footer-note">
            Mini-cloud K3s • Flask • observabilité Prometheus / Grafana • données issues du dépôt et des manifests
        </div>
    </main>
</body>
</html>
"""

STATUS_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }}</title>
    {{ style | safe }}
</head>
<body>
    <main class="container">
        <div class="header">
            <div>
                <span class="badge">Check</span>
                <h1>{{ title }}</h1>
            </div>
            <span class="status-pill {{ status_class }}">{{ status_text }}</span>
        </div>
        <p class="subtitle">{{ message }}</p>
        <div class="actions">
            <a class="button primary" href="/">Retour à l'accueil</a>
            <a class="button secondary" href="/metrics">Métriques</a>
        </div>
    </main>
</body>
</html>
"""


@app.after_request
def count_request(response):
    REQUEST_COUNT.labels(
        method=request.method,
        status=str(response.status_code),
        app=APP_NAME
    ).inc()
    return response


@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, app_name=APP_NAME, style=PAGE_STYLE)


@app.route('/health')
def health():
    """Utilisee par les probes de disponibilite du dashboard"""
    return render_template_string(
        STATUS_TEMPLATE,
        title='Santé du service',
        status_class='ok',
        status_text='OK',
        message='Le service répond correctement et est prêt à recevoir les requêtes.',
        style=PAGE_STYLE
    ), 200


@app.route('/error')
def simulate_error():
    """Route dediee pour declencher une erreur 5xx a la demande
    Utile pour le scenario 'erreurs applicatives' de la Phase 5 :
        curl -k https://app-test.minicloud.local/error
    """
    return render_template_string(
        STATUS_TEMPLATE,
        title='Erreur simulée',
        status_class='error',
        status_text='500',
        message='Une erreur applicative a bien été déclenchée pour tester la supervision et les alertes.',
        style=PAGE_STYLE
    ), 500


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)