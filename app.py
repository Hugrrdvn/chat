import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعداد قاعدة البيانات وتصحيح الرابط تلقائياً ليتوافق مع Render
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.json
        if data and data.get('text'):
            new_msg = Message(
                username=data.get('username', 'زائر ملكي'),
                text=data.get('text')
            )
            db.session.add(new_msg)
            db.session.commit()
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "النص فارغ"})
    
    else:
        messages = Message.query.all()
        result = [{"id": m.id, "username": m.username, "text": m.text} for m in messages]
        return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
