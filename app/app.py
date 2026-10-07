from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total number of HTTP requests received by the application",
    ["method", "endpoint", "status"],
)


@app.after_request
def record_request(response):
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code,
    ).inc()
    return response


@app.route("/")
def home():
    return jsonify(
        {
            "application": "AI-Assisted Cloud Monitoring and Troubleshooting Dashboard",
            "status": "running",
            "message": "COMP 488 project application is running successfully.",
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
        }
    )


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)