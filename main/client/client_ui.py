import requests
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

username = None
room_name = None


def main_menu():
    options = ["Create Chat Room", "Join Chat Room", "Send Message to Room", "View Room Messages", "Quit"]
    if not username:
        options = ["Register", "Login"] + options

    title = f"[bold white on blue]Welcome, {username}![/bold white on blue]" if username else "[bold white on blue]Welcome to the Chat System[/bold white on blue]"
    panel = Panel(
        "\n".join(f"[bold cyan]{i}.[/bold cyan] [yellow]{option}[/yellow]" for i, option in enumerate(options, 1)),
        title=title,
        expand=False
    )
    console.print(panel)
    return Prompt.ask("Enter your choice", choices=[str(i) for i in range(1, len(options) + 1)])

def register():
    console.print("\n[bold green]Register a new user[/bold green]")
    new_username = Prompt.ask("Enter username")
    password = Prompt.ask("Enter password", password=True)
    response = requests.post('http://localhost:5000/register', json={'username': new_username, 'password': password})
    
    try:
        console.print(response.json())
    except requests.exceptions.JSONDecodeError as e:
        console.print(f"[bold red]Error: Failed to decode JSON response.[/bold red]")
        console.print(f"[bold red]Status Code: {response.status_code}[/bold red]")
        console.print(f"[bold red]Response Text: {response.text}[/bold red]")
        console.print(f"[bold red]Error Message: {str(e)}[/bold red]")

def login():
    global username, token
    console.print("\n[bold green]Login[/bold green]")
    login_username = Prompt.ask("Enter username")
    password = Prompt.ask("Enter password", password=True)
    response = requests.post('http://localhost:5000/login', json={'username': login_username, 'password': password})
    if response.status_code == 200:
        console.print("[bold green]Login successful![/bold green]")
        data = response.json()
        username = login_username
        token = data['token']  # 存储JWT令牌
    else:
        console.print("[bold red]Failed to login.[/bold red]")

def create_room():
    global room_name, token
    if not username:
        console.print("\n[bold red]Please log in first.[/bold red]")
        return
    console.print("\n[bold green]Create a new chat room[/bold green]")
    new_room_name = Prompt.ask("Enter room name")
    headers = {'Authorization': f'Bearer {token}'}  # 在请求头中包含JWT令牌
    response = requests.post('http://localhost:5001/create_room', json={'room_name': new_room_name, 'username': username}, headers=headers)
    if response.status_code == 201:
        console.print(response.json())
        room_name = new_room_name
    else:
        console.print(f"[bold red]Failed to create room. Status code: {response.status_code}[/bold red]")
        console.print("[bold red]Response text:[/bold red]", response.text)

def join_room():
    global room_name, token
    if not username:
        console.print("\n[bold red]Please log in first.[/bold red]")
        return
    console.print("\n[bold green]Join a chat room[/bold green]")
    join_room_name = Prompt.ask("Enter room name")
    headers = {'Authorization': f'Bearer {token}'}  # 在请求头中包含JWT令牌
    response = requests.post('http://localhost:5001/join_room', json={'room_name': join_room_name, 'username': username}, headers=headers)
    if response.status_code == 200:
        console.print(response.json())
        room_name = join_room_name
    else:
        console.print(f"[bold red]Failed to join room. Status code: {response.status_code}[/bold red]")
        console.print("[bold red]Response text:[/bold red]", response.text)

def send_to_room():
    global room_name
    if not username:
        console.print("\n[bold red]Please log in first.[/bold red]")
        return
    if not room_name:
        console.print("\n[bold red]Please join a room first.[/bold red]")
        return

    console.print("\n[bold green]Enter your message:[/bold green]")
    message = Prompt.ask()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('http://localhost:5001/send_to_room', json={'room_name': room_name, 'username': username, 'text': message}, headers=headers)

    if response.status_code == 201:
        console.print(response.json())
    else:
        console.print(f"[bold red]Failed to send message. Status code: {response.status_code}[/bold red]")
        console.print("[bold red]Response text:[/bold red]", response.text)

def view_room_messages():
    global room_name
    
    if not room_name:
        console.print("\n[bold red]Please join a room first.[/bold red]")
        return
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'http://localhost:5001/get_room_messages', params={'room_name': room_name}, headers=headers)
    if response.status_code == 200:
        messages = response.json()
        print(messages)
        for message in messages:
            sender_username = message.get('username', 'Unknown') 
            text = message.get('text', '')
            console.print(f"[bold cyan]{sender_username}[/bold cyan] said: {text}")
    else:
        console.print(f"[bold red]Failed to get room messages. Status code: {response.status_code}[/bold red]")
        console.print("[bold red]Response text:[/bold red]", response.text)

def main():
    global username, room_name
    while True:
        choice = main_menu()
        if not username:
            action = {
                '1': register,
                '2': login,
                '3': create_room,
                '4': join_room,
                '5': send_to_room,
                '6': view_room_messages,
                '7': quit
            }.get(choice, lambda: console.print("[bold red]Invalid choice. Please try again.[/bold red]"))
        else:
            action = {
                '1': create_room,
                '2': join_room,
                '3': send_to_room,
                '4': view_room_messages,
                '5': quit
            }.get(choice, lambda: console.print("[bold red]Invalid choice. Please try again.[/bold red]"))

        action()

if __name__ == '__main__':
    main()
