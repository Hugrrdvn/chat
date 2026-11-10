from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, static_folder='.', template_folder='.')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# مسار الصفحة الرئيسية (تأكد أن اسم الملف لديك هو index.html، وإذا كان chat.html قم بتغييره أدناه)
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# استقبال الرسالة وإعادة بثها للجميع فوراً
@socketio.on('chat message')
def handle_chat_message(data):
    emit('chat message', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
