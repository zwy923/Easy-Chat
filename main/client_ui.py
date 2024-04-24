import requests

username = None
room_name = None

def main_menu():
    print("\nWelcome to the Chat System")
    options = ["Register", "Login", "Create Chat Room", "Join Chat Room", "Send Message to Room", "View Room Messages", "Quit"]
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    return input("Enter your choice: ")

def register():
    print("\nRegister a new user")
    new_username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post('http://localhost:5000/register', json={'username': new_username, 'password': password})
    print(response.json())

def login():
    global username
    print("\nLogin")
    login_username = input("Enter username: ")
    password = input("Enter password: ")
    response = requests.post('http://localhost:5000/login', json={'username': login_username, 'password': password})
    if response.status_code == 200:
        print("Login successful!")
        username = login_username
    else:
        print("Failed to login.")

def create_room():
    global room_name
    if not username:
        print("\nPlease log in first.")
        return
    print("\nCreate a new chat room")
    new_room_name = input("Enter room name: ")
    response = requests.post('http://localhost:5001/create_room', json={'room_name': new_room_name, 'username': username})
    if response.status_code == 201:
        print(response.json())
        room_name = new_room_name
    else:
        print(f"Failed to create room. Status code: {response.status_code}")
        print("Response text:", response.text)

def join_room():
    global room_name
    if not username:
        print("\nPlease log in first.")
        return
    print("\nJoin a chat room")
    join_room_name = input("Enter room name: ")
    response = requests.post('http://localhost:5001/join_room', json={'room_name': join_room_name, 'username': username})
    if response.status_code == 200:
        print(response.json())
        room_name = join_room_name
    else:
        print(f"Failed to join room. Status code: {response.status_code}")
        print("Response text:", response.text)

def send_to_room():
    global room_name
    if not username:
        print("\nPlease log in first.")
        return
    if not room_name:
        print("\nPlease join a room first.")
        return

    print("\nEnter your message:")
    message = input()
    response = requests.post('http://localhost:5001/send_to_room', json={'room_name': room_name, 'username': username, 'text': message})

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print("Response text:", response.text)

def view_room_messages():
    global room_name
    
    if not room_name:
        print("\nPlease join a room first.")
        return
    response = requests.get(f'http://localhost:5001/get_room_messages', params={'room_name': room_name})
    if response.status_code == 200:
        messages = response.json()
        for message in messages:
            sender_username = message.get('username', 'Unknown') 
            text = message.get('text', '')
            print(f"{sender_username} said: {text}")
    else:
        print(f"Failed to get room messages. Status code: {response.status_code}")
        print("Response text:", response.text)

def main():
    global username, room_name
    while True:
        choice = main_menu()
        action = {
            '1': register,
            '2': login,
            '3': create_room,
            '4': join_room,
            '5': send_to_room,
            '6': view_room_messages,
            '7': quit
        }.get(choice, lambda: print("Invalid choice. Please try again."))

        action()

if __name__ == '__main__':
    main()
