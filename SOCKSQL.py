# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db, Message, VisitCounter, add_message, list_messages

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "messages.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

db.init_app(app)

with app.app_context():
    db.create_all()
    VisitCounter.get_count()


# ---------- 留言 API ----------
@app.route("/api/messages", methods=["GET"])
def api_list_messages():
    limit = int(request.args.get("limit", 200))
    return jsonify([m.to_dict() for m in list_messages(limit)])


@app.route("/api/messages", methods=["POST"])
def api_add_message():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"ok": False, "error": "missing_fields"}), 400

    msg = add_message(name, email, message)
    return jsonify({"ok": True, "message": msg.to_dict()}), 201


# ---------- 瀏覽計次 API ----------
@app.route("/api/visits", methods=["GET"])
def api_get_visits():
    return jsonify({"count": VisitCounter.get_count()})


@app.route("/api/visits", methods=["POST"])
def api_inc_visits():
    return jsonify({"count": VisitCounter.increment()})


# ---------- 健康檢查 ----------
@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
