from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    def __init__(self):
        # 连接到MongoDB数据库
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['chat_db']
        self.users = self.db.users

    def register_user(self, username, password):
        if self.users.find_one({'username': username}):
            return False  # 用户名已存在
        hashed_password = generate_password_hash(password)
        user_data = {
            'username': username,
            'password': hashed_password
        }
        try:
            self.users.insert_one(user_data)
            return True
        except Exception as e:
            print(f"Failed to register user: {e}")
            return False

    def authenticate_user(self, username, password):
        """ 验证用户登录请求 """
        user = self.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            return True
        return False
