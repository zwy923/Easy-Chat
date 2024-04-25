from flask import Flask, request
from flask_socketio import SocketIO, emit
from user_service import UserService
from chat_service import ChatService

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

user_service = UserService()
chat_service = ChatService()

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('register')
def handle_register(data):
    username = data['username']
    password = data['password']
    if user_service.register_user(username, password):
        emit('response', {'message': 'Registration successful'})
    else:
        emit('response', {'message': 'Registration failed, username might be taken'})

@socketio.on('login')
def handle_login(data):
    username = data['username']
    password = data['password']
    if user_service.authenticate_user(username, password):
        emit('response', {'message': 'Login successful', 'username': username})
    else:
        emit('response', {'message': 'Invalid username or password'})

@socketio.on('send_message')
def handle_message(data):
    sender = data['sender']
    message = data['message']
    recipient = data['recipient']
    if chat_service.send_message(sender, message, recipient):
        emit('new_message', {'sender': sender, 'message': message}, to=recipient)
    else:
        emit('response', {'message': 'Failed to send message'})

@socketio.on('join')
def on_join(data):
    username = data['username']
    socketio.enter_room(request.sid, username)
    emit('response', {'message': f'{username} has entered the chat.'}, room=username)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    socketio.leave_room(request.sid, username)
    emit('response', {'message': f'{username} has left the chat.'}, room=username)

if __name__ == '__main__':
    socketio.run(app, host='localhost', port=5000)



