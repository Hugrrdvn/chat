import os
import uuid
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
# User Connection
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

        history = [dict(message) for message in messages_history]

    emit('load_history', history)

    broadcast_active_users()

    socketio.emit('system_notification', {
        'message': f'✨ انضم {username} إلى الجروب الملكي'
    })


# =====================================
# Send Message
# =====================================

@socketio.on('send_message')
def handle_message(data):

    with data_lock:
        user = active_users.get(request.sid)

    if not user:
        return

    message = str(data.get('message') or '').strip()

    if not message:
        return

    msg_data = {
        'id': str(uuid.uuid4()),
        'username': user['username'],
        'avatar': user['avatar'],
        'message': message,
        'time': datetime.now().strftime('%I:%M %p'),
        'sender_sid': request.sid,
        'status': 'sent'
    }

    with data_lock:
        messages_history.append(msg_data)

        if len(messages_history) > 200:
            messages_history.pop(0)

    socketio.emit('receive_message', msg_data)


# =====================================
# Edit Message
# =====================================

@socketio.on('edit_message')
def handle_edit_message(data):

    message_id = str(data.get('id') or '')
    new_text = str(data.get('message') or '').strip()

    if not message_id or not new_text:
        return

    with data_lock:
        target = next(
            (message for message in messages_history
             if message['id'] == message_id),
            None
        )

        if not target or target['sender_sid'] != request.sid:
            return

        target['message'] = new_text
        target['edited'] = True

        updated_message = dict(target)

    socketio.emit('message_edited', updated_message)


# =====================================
# Delete Message
# =====================================

@socketio.on('delete_message')
def handle_delete_message(data):

    message_id = str(data.get('id') or '')

    if not message_id:
        return

    with data_lock:
        target = next(
            (message for message in messages_history
             if message['id'] == message_id),
            None
        )

        if not target or target['sender_sid'] != request.sid:
            return

        messages_history.remove(target)

    socketio.emit('message_deleted', {
        'id': message_id
    })


# =====================================
# Read Message
# =====================================

@socketio.on('read_message')
def handle_read_message(data):

    message_id = str(data.get('id') or '')

    if not message_id:
        return

    with data_lock:
        target = next(
            (message for message in messages_history
             if message['id'] == message_id),
            None
        )

        if not target:
            return

        target['status'] = 'seen'

    socketio.emit('message_read', {
        'id': message_id
    })


# =====================================
# Update Online Users
# =====================================

def broadcast_active_users():

    with data_lock:
        users_list = list(active_users.values())

    socketio.emit('update_real_users', {
        'users': users_list,
        'count': len(users_list)
    })


# =====================================
# User Disconnect
# =====================================

@socketio.on('disconnect')
def handle_disconnect():

    with data_lock:
        user = active_users.pop(request.sid, None)

    if user:
        broadcast_active_users()

        socketio.emit('system_notification', {
            'message': f'🚪 غادر {user["username"]} الجروب'
        })


# =====================================
# Run Server
# =====================================

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        allow_unsafe_werkzeug=True
    )
