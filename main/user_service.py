from flask import Flask, request, jsonify
from pymongo import MongoClient
import xmlrpc.client
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = MongoClient('localhost', 27017)
db = client.chat_system
users = db.users

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']  # 在实际应用中应加密处理
    user_id = users.insert_one({'username': username, 'password': password}).inserted_id
    return jsonify({'user_id': str(user_id), 'username': username}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = users.find_one({'username': username, 'password': password})
    if user:
        return jsonify({'status': 'success', 'user_id': str(user['_id'])}), 200
    else:
        return jsonify({'status': 'failed'}), 401

if __name__ == '__main__':
    app.run(port=5000)
