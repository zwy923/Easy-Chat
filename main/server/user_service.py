from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

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
    
    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password)
    
    if users.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 409
    
    user_id = users.insert_one({'username': username, 'password': hashed_password}).inserted_id
    token = jwt.encode({'user_id': str(user_id), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users.find_one({'username': data['username']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    token = jwt.encode({'user_id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['SECRET_KEY'])
    return jsonify({'token': token.decode('UTF-8')}), 200

if __name__ == '__main__':
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    app.run(port=5000)
