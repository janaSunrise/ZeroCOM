import socket
import sys
import typing as t

from utils.config import HEADER_LENGTH
from utils.logger import get_logging


def get_header(message: bytes) -> bytes:
    return f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")


def receive_message(client_socket: socket.socket) -> tuple:
    username_header = client_socket.recv(HEADER_LENGTH)

    if not len(username_header):
        print(get_logging("error", "Server has closed the connection."))
        sys.exit(1)

    username_len = int(username_header.decode('utf-8').strip())
    username = client_socket.recv(username_len).decode('utf-8')

    msg_length = int(client_socket.recv(HEADER_LENGTH).decode('utf-8').strip())
    msg = client_socket.recv(msg_length).decode('utf-8')

    return username, msg


def send_message(message: t.Optional[str], client_socket: socket.socket) -> None:
    if message:
        message = message.replace("\n", "").encode("utf-8")
        message_header = get_header(message)

        client_socket.send(message_header + message)
