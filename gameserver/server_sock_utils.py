'''


'''
import logging
import socket
import json
from urllib.request import urlopen

HEADER_SIZE = 10


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
