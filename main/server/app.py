from flask import Flask, request, jsonify
from pymongo import MongoClient


app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.user_service
users = db.users

def validate_user_data(data):
    if not data:
        return False
    if 'username' not in data or 'password' not in data:
        return False
    username = data['username']
    password = data['password']
    if not username or not password:
        return False

    if len(username) < 2 or len(username) > 20:
        return False
    
    if len(password) < 3 or len(password) > 20:
        return False
    
    return True

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not validate_user_data(data):
        return jsonify({'error': 'Invalid data'}), 400
    if users.find_one({'username': data['username']}):
        return jsonify({'error': 'Username already exists'}), 409
    user_id = users.insert_one({'username': data['username'], 'password': data['password']}).inserted_id
    return jsonify({'user_id': str(user_id)}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users.find_one({'username': data['username'], 'password': data['password']})
    if user:
        return jsonify({'status': 'success', 'user_id': str(user['_id'])}), 200
    else:
        return jsonify({'status': 'failed'}), 401

if __name__ == '__main__':
    app.run(port=5000)
