from flask import Flask, jsonify, render_template, request
import sqlite3
import time

app = Flask(__name__)


# تهيئة قاعدة البيانات SQLite
def init_db():
  conn = sqlite3.connect("chat_messages.db")
  cursor = conn.cursor()
  # جدول الرسائل
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            text TEXT,
            avatar TEXT,
            time REAL
        )
    """)
  # جدول الأعضاء والنشاط
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            avatar TEXT,
            online INTEGER,
            last_seen REAL
        )
    """)
  conn.commit()
  conn.close()


init_db()


@app.route("/")
def index():
  return render_template("index.html")


@app.route("/messages", methods=["GET"])
def get_messages():
  conn = sqlite3.connect("chat_messages.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, user, text, avatar, time FROM messages")
  rows = cursor.fetchall()
  conn.close()

  messages = []
  for row in rows:
    messages.append({
        "id": row[0],
        "user": row[1],
        "text": row[2],
        "avatar": row[3],
        "time": row[4],
    })
  return jsonify(messages)


@app.route("/send", methods=["POST"])
def send_message():
  data = request.json
  user = data.get("user")
  text = data.get("text")
  avatar = data.get(
      "avatar", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=900"
  )
  msg_time = time.time()

  if not text or not user:
    return jsonify({"error": "Missing data"}), 400

  conn = sqlite3.connect("chat_messages.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT INTO messages (user, text, avatar, time) VALUES (?, ?, ?, ?)",
      (user, text, avatar, msg_time),
  )
  conn.commit()
  conn.close()
  return jsonify({"status": "success"})


@app.route("/check-name", methods=["POST"])
def check_name():
  data = request.json
  username = data.get("user")
  avatar = data.get("avatar")
  current_time = time.time()

  conn = sqlite3.connect("chat_messages.db")
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR REPLACE INTO members (username, avatar, online, last_seen)"
      " VALUES (?, ?, 1, ?)",
      (username, avatar, current_time),
  )
  conn.commit()
  conn.close()
  return jsonify({"status": "ok"})


@app.route("/members", methods=["GET"])
def get_members():
  conn = sqlite3.connect("chat_messages.db")
  cursor = conn.cursor()
  cursor.execute("SELECT username, avatar, online, last_seen FROM members")
  rows = cursor.fetchall()
  conn.close()

  members = []
  current_time = time.time()
  for row in rows:
    # اعتبار العضو متصلاً إذا كان نشطاً خلال آخر دقيقتين
    is_online = 1 if (current_time - row[3] < 120) else 0
    members.append({
        "username": row[0],
        "avatar": row[1],
        "online": is_online,
    })
  return jsonify(members)


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8080, debug=True)
