from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
# ربط السيرفر مع دعم الاتصال الفوري (CORS مسموح للجميع لضمان عدم حدوث مشاكل اتصال)
socketio = SocketIO(app, cors_allowed_origins="*")

# مسار لجلب الصفحة الرئيسية (إذا كانت ملف HTML في نفس المجلد)
@app.route('/')
def index():
    # استبدل 'index.html' باسم ملف الواجهة عندك إذا كان مختلفاً (مثل chat.html)
    return send_from_directory('.', 'index.html')

# استقبال الرسالة من أي مستخدم وإعادة بثها فوراً لجميع المتصلين
@socketio.on('chat message')
def handle_chat_message(data):
    # data يحتوي على { username, text }
    emit('chat message', data, broadcast=True)

if __name__ == '__main__':
    # Render يحدد المنفذ تلقائياً عبر المتغير البيئي PORT
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
