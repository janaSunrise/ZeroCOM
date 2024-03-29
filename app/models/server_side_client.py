import socket
import typing as t

from .message import Message
from ..config import HEADER_LENGTH
from ..encryption.rsa import RSA


class Client:
    __slots__ = (
        "socket",
        "ip",
        "port",
        "address",
        "username_header",
        "raw_username",
        "username",
        "pub_key_header",
        "pub_key_pem",
        "pub_key",
    )

    def __init__(
        self,
        client_socket: socket.socket,
        address: t.Union[list, tuple],
        username: Message,
        pub_key: Message
    ) -> None:
        self.socket = client_socket

        self.ip, self.port = address
        self.address = f"{address[0]}:{address[1]}"

        self.username_header = username.header
        self.raw_username = username.data
        self.username = self.raw_username.decode()

        if pub_key:
            self.pub_key_header = pub_key.header
            self.pub_key_pem = pub_key.data

            self.pub_key = RSA.load_key_pkcs1(self.pub_key_pem)

    @staticmethod
    def get_header(message: str) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode()
