import socket
import threading
import json
from config import SERVER_HOST, SERVER_PORT
from utils import log_message, log_error, format_message

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}  # 客户端socket与客户信息的映射
        self.channels = {}  # 频道名称与频道内客户端socket的映射
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        log_message(f"Server listening on {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
        except KeyboardInterrupt:
            log_message("Server shutting down.")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        log_message(f"New connection from {client_address}")
        self.clients[client_socket] = {"address": client_address, "nickname": None, "channel": None}

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    self.process_message(client_socket, message)
            except Exception as e:
                log_error(f"Error handling message from {client_address}: {e}")
                break

        log_message(f"Connection closed with {client_address}")
        client_socket.close()
        if self.clients[client_socket]["channel"]:
            self.channels[self.clients[client_socket]["channel"]].remove(client_socket)
        del self.clients[client_socket]

    def process_message(self, client_socket, message):
        message_data = json.loads(message)
        action = message_data.get("action")

        if action == "set_nickname":
            self.clients[client_socket]["nickname"] = message_data["nickname"]
        elif action == "join_channel":
            channel_name = message_data["channel"]
            self.join_channel(client_socket, channel_name)
        elif action == "send_message":
            self.broadcast_message(client_socket, message_data["message"], message_data.get("channel"))

    def join_channel(self, client_socket, channel_name):
        if channel_name not in self.channels:
            self.channels[channel_name] = set()
        old_channel = self.clients[client_socket]["channel"]
        if old_channel:
            self.channels[old_channel].remove(client_socket)
            if not self.channels[old_channel]:  # 如果旧频道为空，则删除
                del self.channels[old_channel]
        self.channels[channel_name].add(client_socket)
        self.clients[client_socket]["channel"] = channel_name
        client_socket.sendall(f"Now you're in channel {channel_name}".encode())

    def broadcast_message(self, sender_socket, message, channel=None):
        if not channel or channel not in self.channels:
            log_error(f"Channel {channel} does not exist.")
            return
        sender_nickname = self.clients[sender_socket]["nickname"]
        formatted_message = format_message(sender_nickname, message)
        for client_socket in self.channels[channel]:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(formatted_message.encode())
                except Exception as e:
                    log_error(f"Failed to send message to {self.clients[client_socket]['address']}: {e}")

if __name__ == "__main__":
    server = ChatServer(SERVER_HOST, SERVER_PORT)
    server.start()
