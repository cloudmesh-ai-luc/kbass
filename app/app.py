from flask import Flask, jsonify

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)