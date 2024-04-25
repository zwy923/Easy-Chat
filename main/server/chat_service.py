from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
import jwt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'your-secret-key'

client = MongoClient('localhost', 27017)
db = client.user_service
chatrooms = db.chatrooms
messages = db.messages
users = db.users

def get_user_by_username(username):
    user = users.find_one({'username': username})
    return user

def authenticate(token):
    if token.startswith("Bearer "):
        token = token[7:]  # 去掉"Bearer"前缀
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        user = users.find_one({'_id': ObjectId(user_id)})
        if user:
            return user['username']
        else:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
@app.route('/create_room', methods=['POST'])
def create_room():
    token = request.headers.get('Authorization')
    username = authenticate(token)
    
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = get_user_by_username(username)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    room_name = data['room_name']
    room_type = data.get('room_type', 'public')
    
    room_id = chatrooms.insert_one({'room_name': room_name, 'room_type': room_type, 'members': [user['_id']]}).inserted_id
    
    return jsonify({'room_id': str(room_id), 'room_name': room_name, 'room_type': room_type}), 201

@app.route('/join_room', methods=['POST'])
def join_room():
    token = request.headers.get('Authorization')
    username = authenticate(token)
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = get_user_by_username(username)
    if not token:
        return jsonify({'error': 'No authorization token provided'}), 401
    
    username = authenticate(token)
    if not username:
        return jsonify({'error': 'Invalid or expired token'}), 403
    
    room_name = request.json.get('room_name')
    if not room_name:
        return jsonify({'error': 'Room name not provided'}), 400
    
    room = chatrooms.find_one({'room_name': room_name})
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    

    if ObjectId(user['_id']) not in room['members']:
        room['members'].append(ObjectId(user['_id']))
        chatrooms.update_one({'_id': room['_id']}, {'$set': {'members': room['members']}})
    
    return jsonify({'message': 'Joined room successfully', 'room_id': str(room['_id'])}), 200


@app.route('/send_to_room', methods=['POST'])
def send_to_room():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No authorization token provided'}), 401

    username = authenticate(token)
    if not username:
        return jsonify({'error': 'Invalid or expired token'}), 403

    room_name = request.json.get('room_name')
    message_text = request.json.get('text')
    if not room_name or not message_text:
        return jsonify({'error': 'Room name or message not provided'}), 400

    room = chatrooms.find_one({'room_name': room_name})
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Assume user must be in the room to send a message
    user = users.find_one({'username': username})
    if ObjectId(user['_id']) not in room['members']:
        return jsonify({'error': 'User is not a member of the room'}), 403

    messages.insert_one({'room_id': room['_id'], 'user_id': user['_id'], 'text': message_text})
    return jsonify({'message': 'Message sent successfully'}), 201

@app.route('/get_room_messages', methods=['GET'])
def get_room_messages():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No authorization token provided'}), 401

    username = authenticate(token)
    if not username:
        return jsonify({'error': 'Invalid or expired token'}), 403

    room_name = request.args.get('room_name')

    if not room_name:
        return jsonify({'error': 'Room name not provided'}), 400

    room = chatrooms.find_one({'room_name': room_name})
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    user = users.find_one({'username': username})
    if ObjectId(user['_id']) not in room['members']:
        return jsonify({'error': 'User is not a member of the room'}), 403

    # 获取消息列表并转换为可以序列化的格式
    message_list = messages.find({'room_id': room['_id']})
    response_data = []
    for message in message_list:
        message_user = users.find_one({'_id': ObjectId(message['user_id'])})
        print(message_user)
        message_username = message_user['username'] if message_user else 'Unknown User'
        message_data = {
            'username': message_username,
            'text': message['text'],
            'created_at': message.get('created_at', '')
        }
        response_data.append(message_data)

    return jsonify(response_data), 200

@app.route('/leave_room', methods=['POST'])
def leave_room():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No authorization token provided'}), 401

    username = authenticate(token)
    if not username:
        return jsonify({'error': 'Invalid or expired token'}), 403

    room_name = request.json.get('room_name')
    if not room_name:
        return jsonify({'error': 'Room name not provided'}), 400

    room = chatrooms.find_one({'room_name': room_name})
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    user = users.find_one({'username': username})
    if ObjectId(user['_id']) not in room['members']:
        return jsonify({'error': 'User is not a member of the room'}), 403

    # Remove user from room's member list
    chatrooms.update_one({'_id': room['_id']}, {'$pull': {'members': ObjectId(user['_id'])}})
    return jsonify({'message': 'Left room successfully'}), 200


if __name__ == '__main__':
    app.run(port=5001)