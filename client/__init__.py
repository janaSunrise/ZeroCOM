import socket
import sys

from utils.config import HEADER_LENGTH
from utils.logger import get_logging
from utils.utils import get_color


def receive_message(sock: socket.socket) -> tuple:
    header = sock.recv(HEADER_LENGTH)

    if not len(header):
        print(get_logging("error", True) + f"{get_color('RED')} Server has closed the connection.")
        sys.exit(1)

    username_len = int(header.decode('utf-8').strip())
    username = sock.recv(username_len).decode('utf-8')

    msg_length = int(sock.recv(HEADER_LENGTH).decode('utf-8').strip())
    msg = sock.recv(msg_length).decode('utf-8')

    return username, msg
