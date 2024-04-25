from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

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
    print(data)
    if not username or not password:
        return False

    if len(username) < 2 or len(username) > 20:
        return False
    
    if len(password) < 3 or len(password) > 20:
        return False
    
    return True

@app.route('/register', methods=['POST'])
def register():
    try:
        print("Received request data:", request.data)
        print("Request content type:", request.content_type)
        
        data = request.get_json()
        print("Parsed JSON data:", data)
        
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid request data'}), 400
        
        if not validate_user_data(data):
            return jsonify({'error': 'Invalid user data'}), 400

        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = {
            'username': data['username'],
            'password': hashed_password
        }
        users.insert_one(new_user)

        token = jwt.encode({'username': data['username']}, app.config['SECRET_KEY'])
        print("Generated token:", token)
        
        return jsonify({'token': token}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = users.find_one({'username': data['username']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    token = jwt.encode({'user_id': str(user['_id']), 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)}, app.config['SECRET_KEY'])
    return jsonify({'token': token}), 200

if __name__ == '__main__':
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    app.run(port=5000)
