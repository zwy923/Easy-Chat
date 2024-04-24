import socket
import json
from threading import Thread

class ChatClient:
    def __init__(self, server_ip='localhost', server_port=5000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = None
        self.is_connected = False

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.server_ip, self.server_port))
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            return False


    def start_receiving_messages(self):
        if self.is_connected:
            Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while self.is_connected:
            try:
                message = self.socket.recv(4096).decode('utf-8')
                if message:
                    print("\nReceived:", message)
                else:
                    self.disconnect()
                    print("Connection closed by the server.")
                    break
            except Exception as e:
                if self.is_connected:
                    print(f"Error receiving data: {e}")
                    self.disconnect()
                break

    def send_message(self, message):
        if not self.is_connected:
            print("Not connected to the server.")
            return
        try:
            self.socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send message: {e}")
            self.disconnect()

    def send_request(self, data):#无响应
        try:
            self.socket.sendall(json.dumps(data).encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            print(f"Error communicating with the server: {e}")
            return None

    def register(self, username, password):
        return self.send_request({"action": "register", "username": username, "password": password})

    def login(self, username, password):
        """ Log in an existing user with the server. """
        return self.send_request({"action": "login", "username": username, "password": password})

    def logout(self):
        """ Send a logout request to the server. """
        self.send_request({"action": "logout"})
        self.disconnect()

    def disconnect(self):
        """ Close the connection to the server. """
        self.is_connected = False
        if self.socket:
            self.socket.close()
            print("Disconnected from the server.")
