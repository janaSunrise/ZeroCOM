import socket
import typing as t

from utils.config import HEADER_LENGTH
from utils.logger import get_logging, get_message_logging
from utils.utils import get_color


class Client:
    def __init__(self, sock: socket.socket, address: list, uname: dict) -> None:
        self.socket = sock
        self.ip = address[0]
        self.port = address[1]
        self.address = f"{address[0]}:{address[1]}"

        self.username_header = uname["header"]
        self.raw_username = uname["data"]
        self.username = self.raw_username.decode("utf-8")

    @staticmethod
    def get_header(message: str) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")


def receive_message(socket_: socket.socket) -> t.Union[dict, bool]:
    try:
        message_header = socket_.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())

        return {"header": message_header, "data": socket_.recv(message_length)}
    except Exception as exc:
        raise exc
        return False


def process_conn(sock: socket.socket, sockets: list, clients: dict) -> bool:
    socket_, address = sock.accept()

    uname = receive_message(socket_)

    client = Client(socket_, address, uname)

    if not uname:
        print(get_logging("error") + f"{get_color('RED')}New connection failed from {client.address}.")
        return False
    else:
        sockets.append(socket_)
        clients[socket_] = client

        print(get_logging("success") + f"{get_color('GREEN')}Accepted new connection requested by {client.username} "
                                       f"[{client.address}].")
        return True


def process_message(sock, sockets: list, clients: dict) -> bool:
    def broadcast(message: dict) -> None:
        for client_socket in clients:
            if client_socket != sock:
                sender_information = client.username_header + client.raw_username
                message_to_send = message["header"] + message["data"]
                client_socket.send(sender_information + message_to_send)

    message = receive_message(sock)

    if not message:
        client = clients[sock]
        print(get_logging("error") + f"{get_color('RED')}Connection closed [{client.username}@{client.address}].")
        sockets.remove(sock)
        clients.pop(sock)
        return False

    client = clients[sock]
    msg = message['data'].decode('utf-8')
    print(get_message_logging(client.username, msg))
    broadcast(message)
