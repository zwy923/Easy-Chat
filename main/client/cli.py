from client import ChatClient  # 确保已经有了client.py中的ChatClient类
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from threading import Thread

console = Console()

def main_menu():

    table = Table(title="Chat Application Main Menu", show_header=True, header_style="bold magenta")
    table.add_column("Option", style="dim", width=12)
    table.add_column("Description")
    table.add_row("1", "Login")
    table.add_row("2", "Register")
    table.add_row("3", "Exit")
    console.print(table)

    choice = Prompt.ask("Choose an option", choices=["1", "2", "3"])
    return choice

def register(chat_client):
    username = Prompt.ask("Enter your desired username")
    password = Prompt.ask("Enter your password", password=True)
    response = chat_client.register(username, password)
    if response and response.get('success', False):
        console.print("[green]Registration successful![/]")
    else:
        console.print(f"[red]Registration failed: {response.get('message', 'Unknown error')}[/]")

def login(chat_client):
    """ 处理用户登录 """
    username = Prompt.ask("Enter your username")
    password = Prompt.ask("Enter your password", password=True)
    if chat_client.login(username, password):
        console.print("[green]Logged in successfully![/]")
        return username
    else:
        console.print("[red]Login failed. Please check your username and password.[/]")
        return None

def start_client():
    chat_client = ChatClient()
    if chat_client.connect_to_server():  # Only proceed if the connection is successful
        while True:
            choice = main_menu()
            if choice == "1":
                user = login(chat_client)
                if user:
                    user_interaction(chat_client, user)
            elif choice == "2":
                register(chat_client)
            elif choice == "3":
                console.print("[bold cyan]Thank you for using the chat application. Goodbye![/]")
                break
    else:
        console.print("[red]Failed to connect to the server. Please check the server status or your network connection and try again.[/]")

def receive_messages(chat_client):
    """ Continuously receive messages from the server and display them """
    while chat_client.is_connected:
        message = chat_client.receive_messages()
        if message:
            console.print(f"\n[blue]{message}[/]")

def user_interaction(chat_client, username):
    """ Handles user inputs and actions after logging in """
    console.print("[green]You can start chatting now! Type 'logout' to exit.[/]")
    Thread(target=lambda: receive_messages(chat_client), daemon=True).start()
    while True:
        message = Prompt.ask(f"[bold magenta]{username}[/]: ")
        if message.lower() == 'logout':
            chat_client.logout()
            console.print("[yellow]You have logged out.[/]")
            break
        chat_client.send_message(message)

if __name__ == "__main__":
    start_client()

