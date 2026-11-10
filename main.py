from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# قائمة لحفظ الرسائل مؤقتاً لتبقى ظاهرة لأي شخص يدخل وللجميع
messages_history = []
# قاموس لتتبع المستخدمين المتصلين حالياً
connected_users = {}

@app.route('/')
def index():
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    print('User connected:', request.sid)
    # إرسال تاريخ الرسائل القديمة للمستخدم فور انضمامه لتظهر له فوراً
    emit('load_history', messages_history)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_users:
        del connected_users[request.sid]
    print('User disconnected:', request.sid)
    # تحديث عدد القائمة والمتصلين للجميع
    emit('update_user_count', len(connected_users), broadcast=True)

@socketio.on('join_chat')
def handle_join(data):
    username = data.get('username', 'مستخدم مجهول')
    connected_users[request.sid] = username
    # إرسال العدد المحدث وقائمة المتصلين الحقيقيين للجميع
    emit('update_user_count', len(connected_users), broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    # حفظ الرسالة في الذاكرة لتكون دائمة ومتاحة للجميع
    messages_history.append(data)
    # إذا تجاوزت الرسائل 500 رسالة، نحذف القديمة ليبقى السيرفر خفيفاً
    if len(messages_history) > 500:
        messages_history.pop(0)
    
    # بث الرسالة فوراً لجميع المتصلين
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
