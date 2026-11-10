from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'royal_chat_secret_key_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

messages_history = []
connected_users = {}

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('join_chat')
def handle_join(data):
    username = data.get('username')
    avatar = data.get('avatar')
    connected_users[request.sid] = {
        'username': username,
        'avatar': avatar
    }
    emit('load_history', messages_history)
    broadcast_users_update()

@socketio.on('send_message')
def handle_send_message(data):
    msg_id = f"msg_{int(time.time() * 1000)}"
    current_time = time.strftime('%I:%M %p', time.localtime())
    current_time = current_time.replace('AM', 'ص').replace('PM', 'م')

    message_obj = {
        'id': msg_id,
        'sender_sid': request.sid,
        'username': data.get('username'),
        'avatar': data.get('avatar'),
        'message': data.get('message'),
        'time': current_time
    }

    messages_history.append(message_obj)
    if len(messages_history) > 100:
        messages_history.pop(0)

    socketio.emit('receive_message', message_obj)

@socketio.on('edit_message')
def handle_edit_message(data):
    msg_id = data.get('id')
    new_text = data.get('message')

    for msg in messages_history:
        if msg['id'] == msg_id:
            msg['message'] = new_text
            break

    socketio.emit('message_edited', {'id': msg_id, 'message': new_text})

@socketio.on('delete_message')
def handle_delete_message(data):
    msg_id = data.get('id')
    global messages_history
    messages_history = [msg for msg in messages_history if msg['id'] != msg_id]
    socketio.emit('message_deleted', {'id': msg_id})

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_users:
        del connected_users[request.sid]
    broadcast_users_update()

def broadcast_users_update():
    users_list = list(connected_users.values())
    socketio.emit('update_real_users', {
        'users': users_list,
        'count': len(users_list)
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

