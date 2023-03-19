'''

 A game server that manages client connections, keeps track of game sessions and states,
 tracks user scores, sends game updates to clients, and handles client requests. Also handles
 user registration, login, password reset, and settings. 


'''
import server_sock_utils
import socket
from datetime import datetime
import json
import database
import threading
import time
import logging
import ssl
import secrets
import server_config
import smtplib
import traceback
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
from lobby import Lobby
from game_session import GameSession

import sys
sys.path.append('../')
import shared.messages as messages

# Define server constants
VERSION = "v0.0.1"
ADDRESS = 'localhost'
PORT = 9999
BUFFER_SIZE = 1024
HEADER_SIZE = 10
START_TIME = time.perf_counter()
logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.DEBUG)
AUTH_EMAILS_ENABLED = False

# Initialize global variables
end = False
connections = []
registered_users = []
total = totalsuccess = 0
lobbies = []

# Dictionary of client sockets and their associated data
'''
client_info = {
    "sock": sock,
    "username": logged_in
}

clients[sock] = client_info
'''
clients = {}

def broadcast_user_list():
    user_list = [client['username'] for _, client in clients.items()]
    print(f"Broadcasting user list: {user_list}")
    for _, client in clients.items():
        user_list_message = messages.UserListUpdateMessage(users=user_list)
        print(f"Sending user list to {client['username']}: {user_list_message.users}")
        server_sock_utils.send_message(client['sock'], user_list_message)




def handshake(sock):
    """
    handshake: Establish a handshake with the client by validating the HELLO and VERSION messages.
    Parameters: sock (socket.socket) - The socket object representing the client connection.
    Returns: None
    Side Effects: Validates the client's HELLO and VERSION messages, updating totalsuccess and appending the client socket to the connections list if successful. Logs warning or error messages as needed.
    Dependencies: json, logging, messages, server_sock_utils
    """
    global totalsuccess
    hello_received = False
    version_received = False
    message = ""

    while not (hello_received and version_received):
        try:
            # Get the message length from the header
            header = sock.recv(HEADER_SIZE)
            if not header:
                logging.warning("Received empty header, closing connection.")
                break

            msg_length = int(header.decode('utf-8').strip())

            # Receive the full message
            message = sock.recv(msg_length).decode('utf-8')

            # Deserialize the message as a dictionary
            message_dict = json.loads(message)

            # Check the message type and handle it accordingly
            if message_dict['type'] == 'HELLO':
                hello_msg = messages.HelloMessage(message_dict['message'])
                logging.info(f"Received HELLO message: {hello_msg.message}")

                if hello_msg.message != "PyPyPy":
                    logging.warning("Client sent invalid header, closing connection.")
                    server_sock_utils.write(sock, "errHeader")
                    break

                hello_received = True

            elif message_dict['type'] == 'VERSION':
                version_msg = messages.VersionMessage(message_dict['version'])
                logging.info(f"Received VERSION message: {version_msg.version}")

                if version_msg.version != "v0.0.1":
                    logging.warning("Client sent invalid version info, closing connection.")
                    server_sock_utils.write(sock, "errVer")
                    break

                version_received = True

            else:
                logging.error(f"Unknown message type: {message_dict['type']}")
                # Handle unknown message types...
        except ValueError as e:
            logging.error(f"Error deserializing message: {e}")
            logging.error(f"Message: {message}")
            # Handle deserialization errors
        except Exception as e:
            logging.error(f"Unexpected error handling message: {e}")
            logging.error(f"Message: {message}")

    if hello_received and version_received:
        logging.info("Received correct hello_msg and version_msg.")
        # Handle correct messages...
        totalsuccess += 1
        logging.info(f"Connection Successful")
        connections.append((sock))
        logging.info(f"New Connection: {sock}")
        logging.info(f"Connections: {connections}")
        return

    else:
        logging.warning("Did not receive correct hello_msg and version_msg.")
        # Handle incorrect messages...
        return

def handle_register(sock, message_dict):
    """
    handle_register: Process client registration request, validate username and email, store new user in the database, and send an authorization email if required.
    Parameters: sock (socket.socket) - The socket object representing the client connection; message_dict (dict) - The dictionary containing the registration message details.
    Returns: False (bool) - Always returns False, indicating the user is not logged in.
    Side Effects: Validates the client's registration information, adds the user to the database, and sends an authorization email if enabled. Logs error messages as needed.
    Dependencies: database, logging, messages, send_authorization_email
    """
    register_msg = messages.RegisterMessage(
        username=message_dict['username'],
        email=message_dict['email'],
        password=message_dict['password']
    )
    logging.info(f"Received REGISTER message:")
    logging.info(f"    Username: {register_msg.username}")
    logging.info(f"    Email: {register_msg.email}")
    logging.info(f"    Password Hash: {register_msg.password}")
    
    # Check for existing username/email
    existing_username = database.get_user_by_username(register_msg.username)
    existing_email = database.get_user_by_email(register_msg.email)

    if existing_username or existing_email:
        # If username/email exists, send error message
        error_message = "Username or email already exists."
        logging.error(error_message)
        # Send error message to client (you may need to modify this line based on your implementation)
        sock.send(error_message.encode('utf-8'))
        return False
    else:
        # If username/email does not exist, add to database
        database.add_user(register_msg.username, register_msg.email, register_msg.password, False)
        
        # Send authorization link email to user
        if AUTH_EMAILS_ENABLED:
            send_authorization_email(register_msg.email)
        # Return false, user is not logged in
        return False

def handle_login(sock, message_dict):
    """
    handle_login: Process client login request, validate email and password, and log in the user if the credentials are correct and the email is confirmed.
    Parameters: sock (socket.socket) - The socket object representing the client connection; message_dict (dict) - The dictionary containing the login message details.
    Returns: username (str) - The username of the logged-in user if successful, or False (bool) if the login is unsuccessful.
    Side Effects: Validates the client's login information, updates the registered_users list, and broadcasts the user list if successful. Sends a login response message to the client. Logs error messages as needed.
    Dependencies: bcrypt, database, logging, messages, server_sock_utils
    """
    login_msg = messages.LoginMessage(
        email=message_dict['email'],
        password=message_dict['password']
    )
    logging.info(f"Received LOGIN message:")
    logging.info(f"    Email: {login_msg.email}")
    logging.info(f"    Password: {login_msg.password}")

    # Check user credentials
    user = database.get_user_by_email(login_msg.email)

    if user:
        # Check if the password hash matches
        stored_password_hash = user[2].encode('utf-8')  # Assuming password_hash is the third field in the users table
        provided_password = login_msg.password.encode('utf-8')

        if bcrypt.checkpw(provided_password, stored_password_hash):
            if user[4]:  # Assuming is_confirmed is the fifth field in the users table
                logging.info(f"{user[1]}: login successful!")
                login_response_msg = messages.LoginResponseMessage(status="success", username=user[1])
                server_sock_utils.send_message(sock, login_response_msg)
                registered_users.append({"username": user[1]})
                logging.info(f"Registered Users: {registered_users}")
                return user[1] 
            else:
                error_message = "Please confirm your email before logging in."
                logging.error(error_message)
                login_response_msg = messages.LoginResponseMessage(status=error_message, username=None)
                server_sock_utils.send_message(sock, login_response_msg)
                return False
        else:
            error_message = "Incorrect password. Please try again."
            logging.error(error_message)
            login_response_msg = messages.LoginResponseMessage(status=error_message, username=None)
            server_sock_utils.send_message(sock, login_response_msg)
            return False
    else:
        error_message = "Email not found. Please register."
        logging.error(error_message)
        login_response_msg = messages.LoginResponseMessage(status=error_message, username=None)
        server_sock_utils.send_message(sock, login_response_msg)
        return False

def handle_login_connection(sock):
    """
    handle_login_connection: Handle the client connection for user registration and login, and process incoming messages accordingly.
    Parameters: sock (socket.socket) - The socket object representing the client connection.
    Returns: logged_in (str or bool) - The username of the logged-in user if successful, or False if the user is not logged in.
    Side Effects: Handles client registration and login messages. Logs warnings and errors as needed.
    Dependencies: json, logging, handle_register, handle_login
    """
    logged_in = False
    while not logged_in:
        try:
            # Get the message length from the header
            header = sock.recv(HEADER_SIZE)
            if not header:
                logging.warning("Received empty header, closing connection.")
                break

            msg_length = int(header.decode('utf-8').strip())

            # Receive the full message
            message = sock.recv(msg_length).decode('utf-8')

            # Deserialize the message as a dictionary
            message_dict = json.loads(message)

            # Check the message type and handle it accordingly
            if message_dict['type'] == 'REGISTER':
                handle_register(sock, message_dict)
                return False

            elif message_dict['type'] == 'LOGIN':
                logged_in = handle_login(sock, message_dict)

            else:
                logging.warning(f"Unexpected message type: {message_dict['type']}")

        except ValueError as e:
            logging.error(f"Error deserializing message: {e}")
            logging.error(f"Message: {message}")
            # Handle deserialization errors
        except socket:
            print(socket)
            traceback.print_exc()
            continue
        except Exception as e:
            logging.error(f"Unexpected error handling message: {e}")
            logging.error(f"Message: {message}")

    return logged_in

def send_authorization_email(email):
    """
    send_authorization_email: Sends an email with an authorization link to the provided email address.
    Parameters: email (str) - The recipient email address.
    Returns: None
    Side Effects: Sends an email to the provided email address with an authorization link.
    Dependencies: smtplib, MIMEText, MIMEMultipart, URLSafeTimedSerializer, server_config.Config, secrets
    """
    sender_email = server_config.Config.MAIL_USERNAME
    sender_password = server_config.Config.MAIL_PASSWORD
    receiver_email = email
    
    s = URLSafeTimedSerializer(secret_key=server_config.Config.SECRET_KEY)
    salt = secrets.token_urlsafe(16)
    auth_token = s.dumps({'email': email, 'salt': salt})

    webserver = "https://localhost:5000"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Authorization Link"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Click the following link to authorize your account: {webserver}/confirm_email?token={auth_token}"
    html = f"""\
    <html>
      <body>
        <p>Click the following link to authorize your account:</p>
        <p><a href="{webserver}/confirm_email?token={auth_token}">{webserver}/confirm_email?token={auth_token}</a></p>
      </body>
    </html>
    """
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def client_handler(sock, username):

    logging.info(f"Entered player function for username: {username}")  # Add this log message
    global registered_users, lobbies
    while True:
        # Get the message length from the header
        header = sock.recv(HEADER_SIZE)
        if not header:
            logging.warning("Received empty header, closing connection.")
            break

        msg_length = int(header.decode('utf-8').strip())

        # Receive the full message
        message = sock.recv(msg_length).decode('utf-8')

        # Deserialize the message as a dictionary
        message_dict = json.loads(message)

        if message_dict['type'] == 'CHAT_MESSAGE':
            chat_msg = messages.ChatMessage(
                username=username,
                message=message_dict['message']
            )
            logging.info(f"Received chat message: {chat_msg.message}")  # Add this log message

            # Store the message in the database
            database.store_chat_message(username, chat_msg.message, datetime.now())

            # Send the message to all connected clients
            for _, other_client in clients.items():
                logging.info(f"Sending chat message to {other_client['sock']}")  # Add this log message
                server_sock_utils.send_message(other_client['sock'], chat_msg)

        elif message_dict['type'] == 'REQUEST_USER_LIST':
            user_list_msg = messages.RequestUserListMessage([user['username'] for user in registered_users])
            server_sock_utils.send_message(sock, user_list_msg)

        elif message_dict['type'] == 'REQUEST_MESSAGE_HISTORY':
            message_history = database.get_messages()
            message_history_msg = messages.RequestMessageHistoryMessage(messages=message_history)
            server_sock_utils.send_message(sock, message_history_msg)

        elif message_dict['type'] == 'CREATE_LOBBY_REQUEST':
            # check to see if lobby name is taken
            # check to see if owner already has a lobby
            # check to see if lobby name is valid
            # check to see if lobby password is valid
            # check to see if lobby max players is valid
            # send LobbyFailedMessage if any of the above are not valid
            # create LobbyCreatedMessage
            # send LobbyCreatedMessage to owner
            owner = message_dict['owner']
            if owner in [lobby.get_owner() for lobby in lobbies]:
                lobby_failed_msg = messages.LobbyFailedMessage(
                    error_message="You already have a lobby."
                )
                server_sock_utils.send_message(sock, lobby_failed_msg)
            
            else:
                lobby_created_msg = messages.CreateLobbyRequestAcceptedMessage(
                    owner=owner,
                )
                server_sock_utils.send_message(sock, lobby_created_msg)


        elif message_dict['type'] == 'CREATE_LOBBY':
            # check to see if lobby name is taken
            # check to see if owner already has a lobby
            # check to see if lobby name is valid
            # check to see if lobby password is valid
            # check to see if lobby max players is valid
            # send LobbyFailedMessage if any of the above are not valid
            # create LobbyCreatedMessage
            # send LobbyCreatedMessage to owner
            owner = message_dict['owner']
            lobby_name = message_dict['lobby_name']
            lobby_password = message_dict['lobby_password']
            max_players = message_dict['max_players']
            game_type = message_dict['game_type']
            if owner in [lobby.get_owner() for lobby in lobbies]:
                lobby_failed_msg = messages.LobbyFailedMessage(
                    error_message="You already have a lobby."
                )
                server_sock_utils.send_message(sock, lobby_failed_msg)
            elif lobby_name in [lobby.get_name() for lobby in lobbies]:
                lobby_failed_msg = messages.LobbyFailedMessage(
                    error_message="Lobby name already taken."
                )
                server_sock_utils.send_message(sock, lobby_failed_msg)
            elif not lobby_name.isalnum():
                lobby_failed_msg = messages.LobbyFailedMessage(
                    error_message="Lobby name must be alphanumeric."
                )
                server_sock_utils.send_message(sock, lobby_failed_msg)
            elif int(max_players) > 10:
                lobby_failed_msg = messages.LobbyFailedMessage(
                    error_message="Maximum players must be less than 10."
                )
                server_sock_utils.send_message(sock, lobby_failed_msg)
            else:
                gamelobby = Lobby(owner=owner, lobby_name=lobby_name, game_type=game_type, max_players=max_players, lobby_password=lobby_password)
                lobby_created_msg = messages.LobbyCreatedMessage(
                    lobby_id=gamelobby.lobby_id,
                    owner=gamelobby.owner,
                    lobby_name=gamelobby.lobby_name,
                    game_type=gamelobby.game_type,
                    max_players=gamelobby.max_players,
                    lobby_password=gamelobby.lobby_password
                )
                for _, other_client in clients.items():
                    server_sock_utils.send_message(other_client['sock'], lobby_created_msg)
                
                lobbies.append(gamelobby)
                logging.info(f"Created lobby {lobby_name} with owner {owner}.")



        elif message_dict['type'] == 'DISCONNECT':
            print("Client disconnected.")
            sock.close()
            disconnected_username = clients[sock]['username']
            del clients[sock]  # Remove the socket from the clients dictionary
            registered_users = [user for user in registered_users if user["username"] != disconnected_username]
            broadcast_user_list()
            break

        elif not message:
            print("Client connection was ended.")
            sock.close()
            disconnected_username = clients[sock]['username']
            del clients[sock]  # Remove the socket from the clients dictionary
            registered_users = [user for user in registered_users if user["username"] != disconnected_username]
            broadcast_user_list()
            break



        # Handle other messages from the client...




def connectionHandlerThread(sock):
    """
    connectionHandlerThread: A function that handles the entire lifecycle of a client connection.
    Parameters: sock (socket.socket) - The socket used for communication with the client.
    Returns: None
    Side Effects:
    1. Performs the handshake process with the client.
    2. Handles the registration and login process.
    3. If logged in, handles client actions until disconnection.
    4. Closes the client's socket and updates the connections list upon disconnection.
    Dependencies: handshake, handle_login_connection, player, logging
    """
    global connections, total, clients
    logging.info("New client is attempting to connect.")
    total += 1
    
    handshake(sock)
    # handle_login_connection returns the username if the login 
    # was successful, otherwise it returns None
    logged_in = handle_login_connection(sock)
    if logged_in:
        logging.info(f"Client {logged_in} has logged in successfully.")
        client_info = {
            "sock": sock,
            "username": logged_in
        }

        clients[sock] = client_info
        broadcast_user_list()
        client_handler(sock, logged_in)
    else:
        logging.warning(f"Client login failed.")

    logging.info(f"Player has Quit")
    
    try:
        connections.remove(sock)
    except:
        pass
    sock.close()

def main():
    """
    main: Initializes and starts the chat server.
    
    This function sets up the main server socket, configures it for SSL, binds it to the specified address and port,
    and listens for incoming client connections. The server will spawn a new connection handler thread for each
    incoming connection, ensuring that multiple clients can be served simultaneously.
    
    Side Effects:
        1. Initializes and configures the main server socket.
        2. Binds the socket to the specified address and port.
        3. Listens for incoming client connections.
        4. Starts connection handler threads for each client connection.
        5. Closes the server socket when the server is stopped.
    """
    # Initialize the main socket
    logging.info(f"Welcome to PyPyPy, {VERSION}\n")
    logging.info("INITIALIZING...")
    logging.info("Starting server with IPv4 (default) configuration.")

    # create a socket object
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # wrap the socket object in an SSL context
    logging.info("Creating SSL context...")
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    logging.info("loading certificate and key files...")
    ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
    logging.info("Wrapping socket with SSL context...")
    server_socket = ssl_context.wrap_socket(server_socket, server_side=True)
    logging.info("Socket wrapped with SSL context.")

    # bind the socket object to a specific address and port
    server_socket.bind((ADDRESS, PORT))

    # listen for incoming connections
    server_socket.listen(16)

    logging.info("Successfully Started.")
    logging.info(f"Accepting connections on port {PORT}\n")

    # Start the connection handler thread
    # This thread will handle all the incoming connections
    while True:
        s, _ = server_socket.accept()
        if end:
            break

        threading.Thread(target=connectionHandlerThread, args=(s,), daemon=True).start()
    server_socket.close()

if __name__ == "__main__":
    main()