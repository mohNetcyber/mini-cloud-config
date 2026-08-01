from flask import Flask, Response, request
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
    return "Mini-cloud K3s - application de test (Flask)\n"


@app.route('/health')
def health():
    """Utilisee par les probes de disponibilite du dashboard"""
    return "OK", 200


@app.route('/error')
def simulate_error():
    """Route dediee pour declencher une erreur 5xx a la demande
    Utile pour le scenario 'erreurs applicatives' de la Phase 5 :
        curl -k https://app-test.minicloud.local/error
    """
    return "Erreur simulee pour test de supervision", 500


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)