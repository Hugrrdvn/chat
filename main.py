from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'royal_secret_key_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# قاعدة بيانات مؤقتة لتخزين المتصلين الحقيقيين والرسائل المرسلة
active_users = {}
messages_history = []

@app.route('/')
def register():
    return render_template('register.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

# حدث عند انضمام مستخدم حقيقي للسيرفر
@socketio.on('join_chat')
def handle_join(data):
    username = data.get('username')
    avatar = data.get('avatar')
    
    active_users[request.sid] = {
        'username': username,
        'avatar': avatar,
        'status': 'متصل الآن'
    }
    
    # تحديث قائمة المتصلين للجميع
    broadcast_active_users()
    
    # إرسال السجل القديم للرسائل للمستخدم الجديد لضمان الاستمرارية
    emit('load_history', messages_history)
    emit('system_notification', {'message': f'✨ انضم "{username}" إلى الجروب الملكي'}, broadcast=True)

# حدث عند إرسال رسالة (تبدأ الصحين بلون رمادي/أسود غامض كلاسيكي وبهدوء تام)
@socketio.on('send_message')
def handle_message(data):
    username = data.get('username')
    avatar = data.get('avatar')
    message = data.get('message')
    timestamp = datetime.now().strftime('%I:%M %p')
    
    msg_data = {
        'username': username,
        'avatar': avatar,
        'message': message,
        'time': timestamp,
        'sender_sid': request.sid,
        'status': 'sent' # تبدأ كمرسلة (صحين رمادي غامض)
    }
    
    messages_history.append(msg_data)
    
    # بث الرسالة بهدوء لكل المتصلين في الجروب
    emit('receive_message', msg_data, broadcast=True)
    
    # محاكاة الاستلام والقراءة التلقائية عبر بايثون لتحويل الصحين إلى أخضر حقيقي بعد الاستلام
    socketio.sleep(2)
    emit('mark_message_delivered', {'sender_sid': request.sid}, broadcast=True)

# حدث عند خروج المستخدم من الشات
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
