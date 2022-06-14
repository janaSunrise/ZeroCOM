from __future__ import annotations

import socket
from queue import Queue

import rsa
from rsa.key import PublicKey

from zerocom.protocol.connection import SocketConnection


class Client:
    def __init__(self, username: str, server_address: tuple[str, int], timeout: float = 3):
        self.username = username
        self.server_host, self.server_port = server_address
        self.timeout = timeout

        # Queue for incoming messages
        self.queue = Queue()

        # Generate the keys needed for RSA encryption
        self.public_key, self.private_key = rsa.newkeys(2048)

        # Connect and transmit username
        socket = self._make_socket(server_address, timeout)
        self.connection = SocketConnection(socket)

        self.connection.write_utf(self.username)
        self.connection.write_utf(PublicKey.save_pkcs1(self.public_key, "PEM").decode())

    @property
    def socket(self) -> socket.socket:
        return self.connection.socket

    @staticmethod
    def _make_socket(server_address: tuple[str, int], timeout: float = 3) -> socket.socket:
        sock = socket.create_connection(server_address, timeout=timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock

    def send(self, message: str) -> None:
        message = message.replace("\n", "")  # TODO: Consider moving to removesuffix (3.9+)
        key_sign = rsa.sign(message.encode(), self.private_key, "SHA-1")

        self.connection.write_utf(key_sign.decode())
        self.connection.write_utf(message)

    def receive(self) -> tuple[str, str]:
        username = self.connection.read_utf()
        msg = self.connection.read_utf()

        return username, msg
