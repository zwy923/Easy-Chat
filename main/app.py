from flask import Flask, request, jsonify
from pymongo import MongoClient
from utils import validate_user_data

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.user_service
users = db.users

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
