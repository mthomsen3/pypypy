'''


'''
import socket
import queue
import json
import logging
import queue
import traceback
from urllib.request import urlopen
import sys
sys.path.append('../')
import shared.messages as messages

HEADER_SIZE = 10
BUFFER_SIZE = 1024
q = queue.Queue()
isdead = True

# A function to get IP address. It can give public IP or private.
def getIp(public):
    if public:
        try:
            ip = urlopen("https://api64.ipify.org").read().decode()
        except:
            ip = "127.0.0.1"  
    else:  
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect(('10.255.255.255', 1))
                ip = s.getsockname()[0]
            except:
                ip = '127.0.0.1'
    return ip


def bgThread(sock):
    """
    This function runs a background thread that continuously receives messages from a server via a socket connection, decodes and formats them into dictionaries, and adds them to a global queue (IO buffer). If an error occurs or a "close" message is received, the thread terminates and sets the global 'isdead' variable to True.
    Args:
    sock (socket.socket): The socket object to receive messages from the server.

    Raises:
    Exception: If there's an error while receiving or processing the message, the function prints the error and its traceback before breaking the loop.
    """
    global isdead
    isdead = False
    while True:
        try:
            header = sock.recv(HEADER_SIZE).decode("utf-8")
            if not header:
                break
            msg_length = int(header.strip())
            msg = sock.recv(msg_length).decode("utf-8")
            print(f"Received message: {msg}")  # Add this line to print the received message
            message_dict = json.loads(msg) 

            # Put the message_dict into the queue
            q.put(message_dict)
            print(f"Adding message to queue: {message_dict}")

        except Exception as e:
            print(f"Error in bgThread: {e}")
            traceback.print_exc()
            break

        if not msg or msg == "close":
            break
        
    isdead = True


# Returns wether background thread is dead and IO buffer is empty.
def isDead():
    return q.empty() and isdead

# A function to read messages sent from the server, reads from queue.
def read():
    if isDead():
        return "close"
    return q.get()

# Check wether a message is readable or not
def readable():
    if isDead():
        return True
    return not q.empty()

# Flush IO Buffer. Returns False if quit command is encountered. True otherwise.
def flush():
    while readable():
        if read() == "close":
            return False
    return True

def send_message(sock, msg):
    """
    Serializes a message object as JSON and sends it to a server via a socket connection, including a header with the message length. Handles specific and general exceptions with logging.

    Args:
    sock (socket.socket): Socket object for server communication.
    msg (object): Message object to be serialized and sent.

    Raises:
    ConnectionResetError, BrokenPipeError, TimeoutError: Logs error and may retry sending the message.
    Exception: Logs unexpected errors during message sending.
    """
    try:
        # Serialize the message object as JSON
        serialized_msg = json.dumps(msg.__dict__)

        # Prepend the header to the message
        header = f"{len(serialized_msg):<{HEADER_SIZE}}".encode('utf-8')
        message = header + serialized_msg.encode('utf-8')

        # Send the message to the server
        sock.sendall(message)

    except (ConnectionResetError, BrokenPipeError, TimeoutError) as e:
        logging.error(f"Error sending message: {e}")
        # Optional: retry sending the message
    except Exception as e:
        logging.error(f"Unexpected error sending message: {e}")
