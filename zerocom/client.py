from __future__ import annotations

from queue import Queue

from zerocom.protocol.connection import SocketConnection


class Client:
    def __init__(self, address: tuple[str, int], username: str, timeout: float = 3) -> None:
        self.host, self.port = address
        self.username = username
        self.connection = SocketConnection.from_address(address, timeout)

        # Queue for incoming messages
        self.queue = Queue()

    def send(self, message: str) -> None:
        self.connection.write_utf(self.username)
        message = message.replace("\n", "")  # TODO: Consider moving to removesuffix (3.9+)
        self.connection.write_utf(message)

    def receive(self) -> tuple[str, str]:
        username = self.connection.read_utf()
        msg = self.connection.read_utf()

        return username, msg
