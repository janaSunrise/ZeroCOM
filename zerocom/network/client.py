from __future__ import annotations

import logging
import socket
from queue import Queue

from zerocom.protocol.connection import SocketConnection

log = logging.getLogger(__name__)


class Client:
    def __init__(self, username: str, server_address: tuple[str, int], timeout: float = 3):
        self.username = username
        self.server_host, self.server_port = server_address
        self.timeout = timeout

        # Queue for incoming messages
        self.queue = Queue()

        # Connect and transmit username
        socket = self._make_socket(server_address, timeout)
        self.connection = SocketConnection(socket)
        self.connection.write_utf(self.username)

    @property
    def socket(self) -> socket.socket:
        return self.connection.socket

    def send(self, message: str) -> None:
        message = message.replace("\n", "")  # TODO: Consider moving to removesuffix (3.9+)
        log.info(f"Sending message {message} to server.")
        self.connection.write_utf(message)

    def receive(self) -> tuple[str, str]:
        username = self.connection.read_utf()
        msg = self.connection.read_utf()

        return username, msg

    @staticmethod
    def _make_socket(server_address: tuple[str, int], timeout: float = 3) -> socket.socket:
        sock = socket.create_connection(server_address, timeout=timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return sock
