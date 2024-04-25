from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from bson.objectid import ObjectId
import jwt

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SECRET_KEY'] = 'your-secret-key'

client = MongoClient('localhost', 27017)
db = client.chat_service
chatrooms = db.chatrooms
messages = db.messages
users = db.users

def authenticate(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/create_room', methods=['POST'])
def create_room():
    token = request.headers.get('Authorization')
    user_id = authenticate(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    room_name = request.json['room_name']
    room_type = request.json.get('room_type', 'public')
    
    if room_type not in ['public', 'private']:
        return jsonify({'error': 'Invalid room type'}), 400
    
    room_id = chatrooms.insert_one({'room_name': room_name, 'room_type': room_type, 'members': [ObjectId(user_id)]}).inserted_id
    return jsonify({'room_id': str(room_id)}), 201

@app.route('/join_room', methods=['POST'])
def join_room():
    token = request.headers.get('Authorization')
    user_id = authenticate(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    room_id = request.json['room_id']
    room = chatrooms.find_one({'_id': ObjectId(room_id)})
    
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    if room['room_type'] == 'private' and ObjectId(user_id) not in room['members']:
        return jsonify({'error': 'Not allowed to join private room'}), 403
    
    chatrooms.update_one({'_id': ObjectId(room_id)}, {'$addToSet': {'members': ObjectId(user_id)}})
    return jsonify({'message': 'Joined room successfully'}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    token = request.headers.get('Authorization')
    user_id = authenticate(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    room_id = request.json['room_id']
    text = request.json['text']
    room = chatrooms.find_one({'_id': ObjectId(room_id)})
    
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    if ObjectId(user_id) not in room['members']:
        return jsonify({'error': 'Not a member of the room'}), 403
    
    messages.insert_one({'room_id': ObjectId(room_id), 'user_id': ObjectId(user_id), 'text': text})
    return jsonify({'message': 'Message sent'}), 200

@app.route('/get_messages', methods=['GET'])
def get_messages():
    token = request.headers.get('Authorization')
    user_id = authenticate(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    room_id = request.args.get('room_id')
    room = chatrooms.find_one({'_id': ObjectId(room_id)})
    
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    if ObjectId(user_id) not in room['members']:
        return jsonify({'error': 'Not a member of the room'}), 403
    
    pipeline = [
        {'$match': {'room_id': ObjectId(room_id)}},
        {'$lookup': {
            'from': 'users',
            'localField': 'user_id',
            'foreignField': '_id',
            'as': 'user'
        }},
        {'$unwind': '$user'},
        {'$project': {
            '_id': 0,
            'text': 1,
            'username': '$user.username',
            'created_at': {'$toDate': '$_id'}
        }},
        {'$sort': {'created_at': 1}}
    ]
    
    messages_list = list(messages.aggregate(pipeline))
    return jsonify(messages_list), 200

@app.route('/leave_room', methods=['POST'])
def leave_room():
    token = request.headers.get('Authorization')
    user_id = authenticate(token)
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    room_id = request.json['room_id']
    room = chatrooms.find_one({'_id': ObjectId(room_id)})
    
    if not room:
        return jsonify({'error': 'Room not found'}), 404
    
    chatrooms.update_one({'_id': ObjectId(room_id)}, {'$pull': {'members': ObjectId(user_id)}})
    return jsonify({'message': 'Left room successfully'}), 200

if __name__ == '__main__':
    app.run(port=5001)