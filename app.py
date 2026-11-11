import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)

# استخدام رابط قاعدة البيانات الخارجي الذي أنشأته على Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://royal_chat_db_user:LhPNTLL0P8w0gLEiet5JKpAyOlLuXo1X@dpg-dbq1khuk1f9s73dbhttg-a.virginia-postgres.render.com/royal_chat_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# جدول تخزين الرسائل في قاعدة بيانات PostgreSQL
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
index():
    # استرجاع آخر الرسائل المحفوظة في قاعدة البيانات لعرضها مباشرة
    messages = Message.query.order_by(Message.id.asc()).all()
    return render_template('index.html', messages=messages)

# استقبال الرسائل عبر الـ WebSocket وإرسالها للجميع مع حفظها في القاعدة
@socketio.on('send_message')
def handle_message(data):
    username = data.get('username')
    text = data.get('text')
    timestamp = datetime.now().strftime('%I:%M %p')
    
    if text:
        # حفظ الرسالة في قاعدة بيانات PostgreSQL الملكية
        new_msg = Message(username=username, text=text, timestamp=timestamp)
        db.session.add(new_msg)
        db.session.commit()
        
        # بث الرسالة فوراً لكل المتواجدين في الجروب
        emit('receive_message', {
            'username': username,
            'text': text,
            'timestamp': timestamp
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
