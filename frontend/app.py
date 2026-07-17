"""Flask frontend for the voice assistant."""
from __future__ import annotations

import os
from urllib.error import URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, render_template


def create_app() -> Flask:
    app = Flask(__name__)

    api_url = os.getenv("VOICE_API_URL", "http://localhost:8000").rstrip("/")
    ws_url = os.getenv("VOICE_WS_URL", api_url.replace("http://", "ws://").replace("https://", "wss://"))

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/config")
    def config():
        return jsonify(
            {
                "apiUrl": api_url,
                "voiceWsBaseUrl": f"{ws_url}/api/v1/voice/ws",
            }
        )

    @app.get("/api-health")
    def api_health():
        request = Request(f"{api_url}/health", headers={"Accept": "application/json"})
        try:
            with urlopen(request, timeout=3) as response:
                return jsonify({"ok": True, "status": response.status})
        except URLError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 503

    @app.get("/health-ui")
    def health_ui():
        return jsonify({"status": "ok", "frontend": True})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", "5001")), debug=True)