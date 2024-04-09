import socket
import threading
import json
from config import SERVER_IP, CLIENT_PORT
from utils import log_message, log_error

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            print(message)
        except Exception as e:
            log_error("Error receiving message: " + str(e))
            break

def send_message(sock, action, **kwargs):
    msg_dict = {"action": action, **kwargs}
    message = json.dumps(msg_dict)
    sock.sendall(message.encode())

def connect_to_server(host, port):
    """try to connnect the server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5) 
    try:
        sock.connect((host, port))
        sock.settimeout(None)  # connection failure
        return sock
    except socket.timeout:
        log_error("Connection timed out")
    except Exception as e:
        log_error(f"Failed to connect to server: {e}")

    return None

def main():
    host = SERVER_IP
    port = CLIENT_PORT

    while True:
        sock = connect_to_server(host, port)
        if sock:
            break  # Successful connection
        retry = input("Failed to connect to the server. Would you like to retry? (y/n): ")
        if retry.lower() != 'y':
            return

    nickname = input("Choose a nickname: ")
    send_message(sock, "set_nickname", nickname=nickname)

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print("Welcome to the chat! Type '/join [channel]' to join a channel, '/list' to list all of channels")
    while True:
        msg = input()
        if msg == "exit":
            break
        if msg.startswith("/join "):
            channel = msg.split(" ", 1)[1]
            send_message(sock, "join_channel", channel=channel)
        elif msg.startswith("/list"):
            send_message(sock, "list_channels")
        elif msg.startswith("@"):
            recipient, message = msg[1:].split(" ", 1)
            send_message(sock, "send_private_message", recipient=recipient, message=message)
        else:
            send_message(sock, "send_message", message=msg)

    sock.close()

if __name__ == "__main__":
    main()
