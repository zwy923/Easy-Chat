import socketio
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

sio = socketio.Client()
console = Console()
logged_in_user = None  # 用于跟踪当前登录的用户

@sio.event
def connect():
    console.print("Connection established", style="green")

@sio.event
def disconnect():
    console.print("Disconnected from server", style="red")

@sio.event
def response(data):
    global logged_in_user
    message_type = data.get('type', '')
    if message_type == 'login_success':
        logged_in_user = data['username']
    elif message_type == 'logout_success':
        logged_in_user = None
    console.print(f"[bold yellow]{data['message']}[/]")

@sio.event
def new_message(data):
    console.print(f"New message from [bold magenta]{data['sender']}[/]: {data['message']}")

def main_menu():
    while True:
        table = Table(title="Chat Application Main Menu", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="dim", width=12)
        table.add_column("Description")
        table.add_row("1", "Login")
        table.add_row("2", "Register")
        if logged_in_user:
            table.add_row("3", "Send Message")
            table.add_row("4", "Logout")
        table.add_row("5", "Exit")
        console.print(table)

        options = ["1", "2", "5"] if not logged_in_user else ["1", "2", "3", "4", "5"]
        choice = Prompt.ask("Choose an option", choices=options)
        if choice == "1":
            login()
        elif choice == "2":
            register()
        elif choice == "3" and logged_in_user:
            send_message()
        elif choice == "4" and logged_in_user:
            logout()
        elif choice == "5":
            console.print("[bold cyan]Thank you for using the chat application. Goodbye![/]")
            break

def register():
    username = Prompt.ask("Enter your desired username")
    password = Prompt.ask("Enter your password", password=True)
    sio.emit('register', {'username': username, 'password': password})

def login():
    username = Prompt.ask("Enter your username")
    password = Prompt.ask("Enter your password", password=True)
    sio.emit('login', {'username': username, 'password': password})

def logout():
    global logged_in_user
    sio.emit('logout', {'username': logged_in_user})
    logged_in_user = None
    console.print("[bold magenta]Logged out successfully![/]")

def send_message():
    if not logged_in_user:
        console.print("Please log in to send messages.", style="red")
        return
    recipient = Prompt.ask("Enter recipient username")
    message = Prompt.ask(f"[bold magenta]{logged_in_user}[/]: ")
    sio.emit('send_message', {'sender': logged_in_user, 'recipient': recipient, 'message': message})

def start_client():
    sio.connect('http://localhost:5000')
    try:
        main_menu()
    finally:
        sio.disconnect()

if __name__ == "__main__":
    start_client()

