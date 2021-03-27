import socket
import typing as t

from utils.config import HEADER_LENGTH


class Client:
    def __init__(self, sock: socket.socket, address: list, uname: dict) -> None:
        self.socket = sock
        self.ip = address[0]
        self.port = address[1]
        self.address = f"{address[0]}:{address[1]}"

        self.username_header = uname["header"]
        self.username = uname["data"].decode("utf-8")

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
    except BaseException:
        return False
