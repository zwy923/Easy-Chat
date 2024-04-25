import socketio
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
import sys

sio = socketio.Client()
console = Console()
logged_in_user = None  # Track the currently logged-in user

@sio.event
def connect():
    console.print("Connection established", style="green")

@sio.event
def disconnect():
    console.print("Disconnected from server", style="red")

@sio.event
def response(data):
    console.print(f"[bold yellow]{data['message']}[/]")
    if 'Login successful' in data['message']:
        global logged_in_user
        logged_in_user = data.get('username')
        console.print("Updating menu for logged-in user...")
        refresh_menu(True)  # Trigger menu refresh after successful login
    else:
        refresh_menu(False)  # Refresh the menu but without reconnecting to main menu

@sio.event
def new_message(data):
    console.print(f"New message from [bold magenta]{data['sender']}[/]: {data['message']}")

def refresh_menu(is_logged_in):
    console.clear()
    if is_logged_in:
        main_menu()

def main_menu():
    table = Table(title="Chat Application Main Menu", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="dim", width=12)
    table.add_column("Description")
    
    if logged_in_user:
        table.add_row("1", "Send Message")
        table.add_row("2", "Logout")
        table.add_row("3", "Exit")
    else:
        table.add_row("1", "Login")
        table.add_row("2", "Register")
        table.add_row("3", "Exit")
    
    console.print(table)
    handle_user_input()

def handle_user_input():
    options = ["1", "2", "3"]
    choice = Prompt.ask("Choose an option", choices=options)
    
    if choice == "1" and not logged_in_user:
        login()
    elif choice == "2" and not logged_in_user:
        register()
    elif choice == "1" and logged_in_user:
        send_message()
    elif choice == "2" and logged_in_user:
        logout()
    elif choice == "3":
        console.print("[bold cyan]Thank you for using the chat application. Goodbye![/]")
        sio.disconnect()
        sys.exit(0)  # Ensure clean exit

def register():
    username = Prompt.ask("Enter your desired username")
    password = Prompt.ask("Enter your password", password=True)
    sio.emit('register', {'username': username, 'password': password})

def login():
    global logged_in_user
    username = Prompt.ask("Enter your username")
    password = Prompt.ask("Enter your password", password=True)
    sio.emit('login', {'username': username, 'password': password})

def logout():
    global logged_in_user
    sio.emit('logout', {'username': logged_in_user})
    logged_in_user = None

def send_message():
    recipient = Prompt.ask("Enter recipient username")
    message = Prompt.ask(f"[bold magenta]{logged_in_user}[/]: ")
    sio.emit('send_message', {'sender': logged_in_user, 'recipient': recipient, 'message': message})

def start_client():
    sio.connect('http://localhost:5000')
    main_menu()
    sio.wait()

if __name__ == "__main__":
    start_client()

