import socketio
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

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

@sio.event
def new_message(data):
    console.print(f"New message from [bold magenta]{data['sender']}[/]: {data['message']}")

def main_menu():
    while True:
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

        options = ["1", "2", "3"]
        choice = Prompt.ask("Choose an option", choices=options)
        
        handle_menu_choice(choice)

def handle_menu_choice(choice):
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
        exit()

def register():
    username = Prompt.ask("Enter your desired username")
    password = Prompt.ask("Enter your password", password=True)
    sio.emit('register', {'username': username, 'password': password})

def login():
    username = Prompt.ask("Enter your username")
    password = Prompt.ask("Enter your password", password=True)
    sio.emit('login', {'username': username, 'password': password})

def logout():
    sio.emit('logout', {'username': logged_in_user})
    global logged_in_user
    logged_in_user = None  # Reset the login state after logging out

def send_message():
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

