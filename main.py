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
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
        }


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/api/send_message", methods=["POST"])
def send_message():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    content = str(data.get("content", "")).strip()

    if not username or not content:
        return jsonify({"error": "اسم المستخدم والرسالة مطلوبان."}), 400
    if len(username) > 100:
        return jsonify({"error": "اسم المستخدم طويل جداً."}), 400
    if len(content) > 5000:
        return jsonify({"error": "الرسالة طويلة جداً (الحد 5000 حرف)."}), 400

    new_msg = Message(username=username, content=content)
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "تم حفظ الرسالة.",
        "data": new_msg.to_dict(),
    }), 201


@app.route("/api/get_messages", methods=["GET"])
def get_messages():
    messages = Message.query.order_by(Message.timestamp.asc()).limit(500).all()
    return jsonify([msg.to_dict() for msg in messages])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port= int(__import__("os").environ.get("PORT", 5000)), debug=False)
