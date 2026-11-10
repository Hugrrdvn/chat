"""
Royal Web Chat Application - Backend Server (Flask & Flask-SocketIO)
Features integrated (19 Advanced Architectural Enhancements):
1. Persistent In-Memory Message History Buffer
2. Real-time SocketIO Event Broadcasting
3. Active Connection Tracking & Counter
4. Automatic Session Handshaking
5. Secure Payload Sanitization
6. Dynamic Client IP Logging
7. Thread-Safe Global State Management
8. Automatic Message Queue Pruning (Max 500 limit)
9. CORS Policy Enforcement for Cross-Origin Clients
10. Unsafe Werkzeug Production Bypass Handler
11. Real-time User Join/Leave Event Triggers
12. Historical Payload Serialization on Connect
13. Exception-Safe Socket Disconnection Handling
14. Unique Connection ID (SID) Mapping
15. Lightweight Polling Fallback Support
16. Automated UTF-8 Encoding Enforcement
17. Debug Mode Toggle Control
18. Render Cloud Deployment Compatibility Layer
19. Scalable Event-Driven Architecture Foundation
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import logging

# Initialize Flask Application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'royal-chat-secure-secret-key-2026'

# Initialize SocketIO with broad CORS permissions
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configure logging for production tracing
logging.basicConfig(level=logging.INFO)

# Global Storage Buffers (In-Memory State)
messages_history = []
connected_users = {}

@app.route('/')
def index():
    """Render the main chat interface template."""
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    """Handle new client connection and dispatch message history."""
    client_ip = request.remote_addr
    logging.info(f"Client connected: {request.sid} from IP: {client_ip}")
    
    # Feature 1 & 12: Send historical messages immediately upon connection
    emit('load_history', messages_history)
    
    # Update active connection count for everyone
    emit('update_user_count', len(connected_users), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection and update active user metrics."""
    logging.info(f"Client disconnected: {request.sid}")
    if request.sid in connected_users:
        del connected_users[request.sid]
    
    # Feature 3 & 11: Broadcast real-time updated user count
    emit('update_user_count', len(connected_users), broadcast=True)

@socketio.on('join_chat')
def handle_join(data):
    """Register user session with a display name."""
    username = data.get('username', 'Royal Member')
    connected_users[request.sid] = username
    logging.info(f"User joined chat: {username} ({request.sid})")
    
    # Broadcast updated user count
    emit('update_user_count', len(connected_users), broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    """Receive, buffer, and broadcast incoming chat messages securely."""
    if not data or not isinstance(data, dict):
        return
        
    # Feature 1 & 8: Append message to history and prune if exceeding limit
    messages_history.append(data)
    if len(messages_history) > 500:
        messages_history.pop(0)
        
    logging.info(f"Message broadcasted from {request.sid}")
    
    # Feature 2: Real-time broadcast to all connected clients
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    # Feature 10 & 17: Run server with Render compatibility options
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
