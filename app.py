import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# جدول الرسائل المحفوظة للأبد
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# جدول الأعضاء الحقيقيين والمتصلين
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# صفحة تسجيل الدخول (الصفحة الرئيسية)
@app.route('/')
def login():
    return render_template('index.html')

# صفحة الشات الملكي
@app.route('/chat')
def chat_page():
    return render_template('chat.html')

@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.json
        if data and data.get('text'):
            new_msg = Message(
                username=data.get('username', 'زائر ملكي'),
                text=data.get('text')
            )
            db.session.add(new_msg)
            db.session.commit()
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "النص فارغ"})
    else:
        messages = Message.query.order_by(Message.id.asc()).all()
        result = [{"id": m.id, "username": m.username, "text": m.text} for m in messages]
        return jsonify(result)

@app.route('/members', methods=['GET', 'POST'])
def handle_members():
    if request.method == 'POST':
        data = request.json
        if data and data.get('username'):
            uname = data.get('username')
            member = Member.query.filter_by(username=uname).first()
            if member:
                member.last_seen = datetime.utcnow()
            else:
                new_member = Member(username=uname)
                db.session.add(new_member)
            db.session.commit()
            return jsonify({"status": "success"})
    
    all_members = Member.query.all()
    members_list = [{"username": m.username} for m in all_members]
    return jsonify({
        "total_members": len(all_members) + 1325,
        "online_count": len(all_members),
        "members": members_list
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
