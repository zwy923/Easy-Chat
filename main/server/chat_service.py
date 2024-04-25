from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.chat_system
chatrooms = db.chatrooms  # Chat room collection
messages = db.messages  # Messages collection
users = db.users  # Assuming there's a users collection

@app.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.json['room_name']
    username = request.json.get('username')  # Get the username from request
    user = users.find_one({'username': username})  # Find the user by username
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    room_id = chatrooms.insert_one({'room_name': room_name, 'members': [user['_id']]}).inserted_id
    return jsonify({'message': 'Room created successfully', 'room_id': str(room_id)}), 201

@app.route('/join_room', methods=['POST'])
def join_room():
    room_name = request.json['room_name']
    username = request.json['username']
    room = chatrooms.find_one({'room_name': room_name})  # Find the room by name
    user = users.find_one({'username': username})  # Find the user by username

    if not room or not user:
        return jsonify({'error': 'Room or user not found'}), 404
    
    chatrooms.update_one({'_id': room['_id']}, {'$addToSet': {'members': user['_id']}})
    return jsonify({'message': 'Joined room successfully'}), 200

@app.route('/send_to_room', methods=['POST'])
def send_to_room():
    room_name = request.json['room_name']
    username = request.json['username']
    text = request.json['text']
    room = chatrooms.find_one({'room_name': room_name})
    user = users.find_one({'username': username})

    if not room or not user:
        return jsonify({'error': 'Room or user not found'}), 404
    
    messages.insert_one({'room_id': room['_id'], 'user_id': user['_id'], 'text': text})
    return jsonify({'message': 'Message sent'}), 200

@app.route('/get_room_messages', methods=['GET'])
def get_room_messages():
    room_name = request.args.get('room_name')
    room = chatrooms.find_one({'room_name': room_name})

    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Start the aggregation pipeline
    pipeline = [
        {'$match': {'room_id': room['_id']}},
        {'$lookup': {
            'from': 'users',
            'localField': 'user_id',
            'foreignField': '_id',
            'as': 'user_info'
        }},
        {'$unwind': {
            'path': '$user_info',
            'preserveNullAndEmptyArrays': True
        }},
        {'$project': {
            'text': 1,
            'username': '$user_info.username',
            # Ensure all fields are serializable
        }}
    ]
    room_messages = messages.aggregate(pipeline)

    # Convert the messages to a list and make sure all ObjectId instances are turned into strings
    try:
        room_messages_list = []
        for message in room_messages:
            message['_id'] = str(message['_id'])  # Convert ObjectIds to strings
            if 'user_info' in message:
                message['user_info']['_id'] = str(message['user_info']['_id'])
            room_messages_list.append(message)

        return jsonify(room_messages_list), 200
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': 'An error occurred while retrieving messages'}), 500


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5001)
