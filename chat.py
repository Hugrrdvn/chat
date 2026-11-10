from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['SECRET_KEY'] = 'my-secret-key'

# تهيئة السيرفر مع السماح بالاتصالات الخارجية
socketio = SocketIO(app, cors_allowed_origins="*")

# مسار الصفحة الرئيسية (تأكد أن اسم ملف الـ HTML لديك مطابق، مثل chat.html أو index.html)
@app.route('/')
def index():
    return send_from_directory('.', 'chat.html')

# استقبال وإعادة بث الرسائل للجميع فوراً
@socketio.on('chat message')
def handle_chat_message(data):
    emit('chat message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port)
