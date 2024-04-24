from flask import Blueprint, request, jsonify
from user_service import UserService
from chat_service import ChatService

api = Blueprint('api', __name__)

user_service = UserService()
chat_service = ChatService()

@api.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    if user_service.register_user(username, password):
        return jsonify({'message': 'Registration successful'}), 200
    else:
        return jsonify({'message': 'Registration failed, username might be taken'}), 400

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if user_service.authenticate_user(username, password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

@api.route('/send', methods=['POST'])
def send_message():
    data = request.json
    sender = data.get('sender')
    message = data.get('message')
    recipient = data.get('recipient')
    if chat_service.send_message(sender, message, recipient):
        return jsonify({'message': 'Message sent'}), 200
    else:
        return jsonify({'message': 'Failed to send message'}), 400

@api.route('/receive', methods=['POST'])
def receive_message():
    data = request.json
    recipient = data.get('recipient')
    messages = chat_service.receive_messages(recipient)
    return jsonify({'messages': messages}), 200