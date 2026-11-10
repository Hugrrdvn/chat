import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'royal_secret_key_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

active_users = {}
messages_history = []

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('join_chat')
def handle_join(data):
    username = data.get('username') or "عضو ملكي"
    avatar = data.get('avatar') or "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=900"
    
    active_users[request.sid] = {
        'username': username,
        'avatar': avatar,
        'status': 'متصل الآن'
    }
    
    broadcast_active_users()
    emit('load_history', messages_history)
    emit('system_notification', {'message': f'✨ انضم "{username}" إلى الجروب الملكي'}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    username = data.get('username') or "عضو ملكي"
    avatar = data.get('avatar') or "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=900"
    message = data.get('message')
    if not message:
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
    
    messages_history.append(msg_data)
    if len(messages_history) > 100:
        messages_history.pop(0)
        
    emit('receive_message', msg_data, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in active_users:
        user = active_users.pop(request.sid)
        broadcast_active_users()
        emit('system_notification', {'message': f'🚪 غادر "{user["username"]}" الجروب'}, broadcast=True)

def broadcast_active_users():
    users_list = list(active_users.values())
    total_online = len(users_list)
    emit('update_real_users', {
        'users': users_list,
        'count': total_online
    }, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
