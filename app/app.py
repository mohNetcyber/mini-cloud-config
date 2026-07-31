from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Expose automatiquement /metrics avec http_requests_total{method, status, path}
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application de test - mini-cloud K3s', version='1.0.0')


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)