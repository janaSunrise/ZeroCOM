from __future__ import annotations

import socket
import sys
from queue import Queue

from .config import Config
from .utils.header import get_header


class Client:
    def __init__(self, address: tuple[str, int], username: str) -> None:
        self.host, self.port = address
        self.username = username

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Queue for incoming messages
        self.queue = Queue()

    # Region: Connection related logic.
    def connect(self, address: tuple[str, int]) -> None:
        try:
            self.socket.connect(address)
        except ConnectionRefusedError as exc:
            raise exc  # Re-raise, handle later using logging.

    def disconnect(self) -> None:
        self.socket.close()

    def reconnect(self) -> None:
        self.disconnect()
        self.connect((self.host, self.port))
    # Endregion.

    # Region: Message related logic.
    def send(self, message: str) -> None:
        message_bytes = message.replace("\n", "").encode()
        message_header = get_header(message_bytes, Config.HEADER_LENGTH)

        username_bytes = self.username.encode()
        username_header = get_header(username_bytes, Config.HEADER_LENGTH)

        self.socket.send(username_header + username_bytes)
        self.socket.send(message_header + message_bytes)

    def receive(self) -> tuple[str, str]:
        username_header = self.socket.recv(Config.HEADER_LENGTH)

        if not len(username_header):
            sys.exit(1)

        username_len = int(username_header.decode().strip())
        username = self.socket.recv(username_len).decode()

        msg_length = int(self.socket.recv(Config.HEADER_LENGTH).decode().strip())
        msg = self.socket.recv(msg_length).decode()

        return username, msg
    # Endregion.
