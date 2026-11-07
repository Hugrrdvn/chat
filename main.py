import os
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chat_messages.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    avatar = db.Column(db.Text, nullable=True)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.msg_id,
            "user": self.username,
            "text": self.content,
            "avatar": self.avatar or "https://i.imgur.com/6VBx3io.png",
            "time": self.timestamp.timestamp(),
        }

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/check-name", methods=["POST"])
def check_name():
    data = request.get_json(silent=True) or {}
    username = str(data.get("user", "")).strip()

    if len(username) < 3 or len(username) >= 10:
        return jsonify({"taken": True, "error": "طول الاسم غير مسموح"})

    return jsonify({"taken": False})

@app.route("/messages", methods=["GET"])
def get_messages():
    messages = Message.query.order_by(Message.timestamp.asc()).limit(500).all()
    return jsonify([msg.to_dict() for msg in messages])

@app.route("/send", methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    username = str(data.get("user", "")).strip()
    content = str(data.get("text", "")).strip()
    avatar = data.get("avatar", "")

    if not username or not content:
        return jsonify({"error": "الاسم والرسالة مطلوبان."}), 400

    unique_id = str(time.time())
    new_msg = Message(msg_id=unique_id, username=username, content=content, avatar=avatar)
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({
        "status": "success",
        "data": new_msg.to_dict(),
    }), 201

@app.route("/edit", methods=["POST"])
def edit_message():
    data = request.get_json(silent=True) or {}
    msg_id = data.get("id")
    new_text = str(data.get("text", "")).strip()
    username = data.get("user")

    msg = Message.query.filter_by(msg_id=msg_id, username=username).first()
    if msg:
        msg.content = new_text + " (معدلة)"
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "غير مسموح بالتعديل"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
