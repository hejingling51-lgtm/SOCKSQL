# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db, Message, VisitCounter, add_message, list_messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build_db_uri():
    """優先使用 DATABASE_URL（Render PostgreSQL / Neon），否則退回 SQLite。"""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        # 統一用 psycopg3 驅動（支援 Python 3.14）
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url
    # 本機開發備援：SQLite
    return f"sqlite:///{os.path.join(BASE_DIR, 'messages.db')}"


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = build_db_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    with app.app_context():
        db.create_all()
        VisitCounter.get_count()

    @app.route("/api/messages", methods=["GET"])
    def api_list_messages():
        try:
            limit = max(1, min(int(request.args.get("limit", 200)), 500))
        except (TypeError, ValueError):
            limit = 200
        return jsonify([m.to_dict() for m in list_messages(limit)])

    @app.route("/api/messages", methods=["POST"])
    def api_add_message():
        data = request.get_json(silent=True) or {}
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        message = (data.get("message") or "").strip()

        if not name or not email or not message:
            return jsonify({"ok": False, "error": "missing_fields"}), 400
        if "@" not in email or "." not in email.split("@")[-1]:
            return jsonify({"ok": False, "error": "invalid_email"}), 400
        if len(name) > 80 or len(email) > 160 or len(message) > 2000:
            return jsonify({"ok": False, "error": "too_long"}), 400

        msg = add_message(name, email, message)
        return jsonify({"ok": True, "message": msg.to_dict()}), 201

    @app.route("/api/visits", methods=["GET"])
    def api_get_visits():
        return jsonify({"count": VisitCounter.get_count()})

    @app.route("/api/visits", methods=["POST"])
    def api_inc_visits():
        return jsonify({"count": VisitCounter.increment()})

    @app.route("/api/health", methods=["GET"])
    def api_health():
        return jsonify({"ok": True})

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return jsonify({"ok": False, "error": "internal_error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)