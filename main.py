import os
from datetime import datetime
from threading import Lock

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'royal_secret_key_2026'

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=True,
    engineio_logger=True
)

active_users = {}
messages_history = []
data_lock = Lock()


@app.route('/')
def index():
    return render_template('chat.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


# =====================================
# دخول الأعضاء
# =====================================

@socketio.on('join_chat')
def handle_join(data):

    username = data.get('username') or 'عضو ملكي'

    avatar = data.get('avatar') or ''

    with data_lock:

        active_users[request.sid] = {
            'username': username,
            'avatar': avatar,
            'status': 'متصل الآن'
        }

        history = list(messages_history)

    # إرسال سجل الرسائل للعضو الجديد
    emit('load_history', history)

    # تحديث عدد المتصلين للجميع
    broadcast_active_users()

    # إشعار دخول العضو
    socketio.emit(
        'system_notification',
        {
            'message': f'✨ انضم {username} إلى الجروب الملكي'
        }
    )

    print(f'عضو جديد: {username}')


# =====================================
# استقبال وإرسال الرسائل
# =====================================

@socketio.on('send_message')
def handle_message(data):

    username = data.get('username') or 'عضو ملكي'

    avatar = data.get('avatar') or ''

    message = str(data.get('message') or '').strip()

    if not message:
        return

    # التأكد من أن المرسل متصل
    with data_lock:
        if request.sid not in active_users:
            print('رفض رسالة من اتصال غير مسجل')
            return

    timestamp = datetime.now().strftime('%I:%M %p')

    msg_data = {
        'username': username,
        'avatar': avatar,
        'message': message,
        'time': timestamp,
        'sender_sid': request.sid,
        'status': 'sent'
    }

    # حفظ الرسالة
    with data_lock:

        messages_history.append(msg_data)

        if len(messages_history) > 200:
            messages_history.pop(0)

    # أهم جزء:
    # إرسال الرسالة لجميع المتصلين في الموقع
    # بما في ذلك الشخص الذي أرسل الرسالة

    socketio.emit(
        'receive_message',
        msg_data
    )

    print(
        f'تم بث الرسالة من {username}: {message}'
    )


# =====================================
# تحديث المتصلين
# =====================================

def broadcast_active_users():

    with data_lock:
        users_list = list(active_users.values())

    count = len(users_list)

    socketio.emit(
        'update_real_users',
        {
            'users': users_list,
            'count': count
        }
    )

    print(f'المتصلون الآن: {count}')


# =====================================
# مغادرة الأعضاء
# =====================================

@socketio.on('disconnect')
def handle_disconnect():

    with data_lock:
        user = active_users.pop(request.sid, None)

    if user:

        broadcast_active_users()

        socketio.emit(
            'system_notification',
            {
                'message': f'🚪 غادر {user["username"]} الجروب'
            }
        )

        print(f'غادر العضو: {user["username"]}')


# =====================================
# تشغيل السيرفر
# =====================================

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        allow_unsafe_werkzeug=True
    )
