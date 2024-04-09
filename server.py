import socket
import threading
import json
from config import SERVER_HOST, SERVER_PORT
from utils import log_message, log_error, format_message

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.channels = {"public": set()}
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
        self.clients[client_socket] = {"address": client_address, "nickname": None, "channel": "public"}
        self.channels["public"].add(client_socket)  # 将新客户端加入默认频道public

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
            self.broadcast_message(client_socket, message_data["message"], self.clients[client_socket]["channel"])
        elif action == "send_private_message":
            self.send_private_message(client_socket, message_data["recipient"], message_data["message"])
        elif action == "list_channels":
            self.list_channels(client_socket)

    def join_channel(self, client_socket, channel_name):
        if self.clients[client_socket]["channel"] in self.channels:
            self.channels[self.clients[client_socket]["channel"]].remove(client_socket)
        if channel_name not in self.channels:
            self.channels[channel_name] = set()
        self.channels[channel_name].add(client_socket)
        self.clients[client_socket]["channel"] = channel_name
        client_socket.sendall(f"Now you're in channel {channel_name}".encode())

    def broadcast_message(self, sender_socket, message, channel):
        sender_nickname = self.clients[sender_socket]["nickname"]
        formatted_message = format_message(sender_nickname, message)
        for client_socket in self.channels[channel]:
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(formatted_message.encode())
                except Exception as e:
                    log_error(f"Failed to send message to {self.clients[client_socket]['address']}: {e}")
                    
    def send_private_message(self, sender_socket, recipient_nickname, message):
        sender_nickname = self.clients[sender_socket]["nickname"]
        recipient_socket = None
        for client, info in self.clients.items():
            if info["nickname"] == recipient_nickname:
                recipient_socket = client
                break

        if recipient_socket:
            formatted_message = f"Private from {sender_nickname}: {message}"
            try:
                recipient_socket.sendall(formatted_message.encode())
            except Exception as e:
                log_error(f"Failed to send private message to {recipient_nickname}: {e}")
        else:
            error_message = f"User {recipient_nickname} not found."
            try:
                sender_socket.sendall(error_message.encode())
            except Exception as e:
                log_error(f"Failed to notify {sender_nickname} about the error: {e}")

    def list_channels(self, client_socket):
        """向请求客户端发送当前所有频道的列表。"""
        channels_list = list(self.channels.keys())
        message = "Available channels: " + ", ".join(channels_list)
        try:
            client_socket.sendall(message.encode())
        except Exception as e:
            log_error(f"Failed to send channels list: {e}")

if __name__ == "__main__":
    server = ChatServer(SERVER_HOST, SERVER_PORT)
    server.start()
