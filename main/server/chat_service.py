from pymongo import MongoClient
from datetime import datetime

class ChatService:
    def __init__(self):
        # 连接到MongoDB数据库
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['chat_db']
        self.messages = self.db.messages

    def send_message(self, sender, message, recipient):
        """ 存储消息到数据库 """
        message_data = {
            'sender': sender,
            'recipient': recipient,
            'message': message,
            'timestamp': datetime.now()
        }
        try:
            self.messages.insert_one(message_data)
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False

    def receive_messages(self, recipient):
        """ 从数据库检索消息 """
        try:
            message_list = list(self.messages.find({'recipient': recipient}))
            # 格式化消息输出
            formatted_messages = [
                f"{msg['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {msg['sender']}: {msg['message']}"
                for msg in message_list
            ]
            return formatted_messages
        except Exception as e:
            print(f"Failed to receive messages: {e}")
            return []
