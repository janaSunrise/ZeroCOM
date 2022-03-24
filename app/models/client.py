import socket
import sys
import time
import typing as t

from ..config import HEADER_LENGTH
from ..encryption.rsa import RSA
from ..mixins.logging import LoggingMixin
from ..utils import on_startup


class Client(LoggingMixin):
    __slots__ = (
        "host",
        "port",
        "username",
        "socket",
        "start_timer",
        "startup_duration",
        "PRIVATE_KEY",
        "PUBLIC_KEY",
        "motd"
    )

    def __init__(self, address: tuple, username: str) -> None:
        self.host, self.post = address
        self.username = username

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.start_timer = time.perf_counter()
        self.startup_duration = None

        self.PUBLIC_KEY, self.PRIVATE_KEY = RSA.generate_keys(512)

        self.motd = None

    @staticmethod
    def get_header(message: bytes) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode()

    def connect(self) -> None:
        try:
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            on_startup("Client")

            self.logger.error("Connection could not be established. Invalid HOST/PORT.")
            sys.exit(1)

    def disconnect(self) -> None:
        self.socket.close()

    def display_connected_banner(self) -> None:
        end = time.perf_counter()
        self.startup_duration = round((end - self.start_timer) * 1000, 2)

        on_startup("Client", self.startup_duration, motd=self.motd)

        self.logger.success(f"Connected to remote host at [{self.host}:{self.port}]")

    def initialize(self) -> None:
        # Send the specified uname.
        uname = self.username.encode()
        uname_header = self.get_header(uname)

        # Key auth
        exported_public_key = RSA.export_key_pkcs1(self.PUBLIC_KEY, "PEM")
        public_key_header = self.get_header(exported_public_key)

        # Send the message
        self.socket.send(uname_header + uname)
        self.socket.send(public_key_header + exported_public_key)

        # Receive the MOTD
        motd_len = int(self.socket.recv(HEADER_LENGTH).decode().strip())
        self.motd = self.socket.recv(motd_len).decode().strip()

        # Set blocking to false.
        self.socket.setblocking(False)

        # Display banner
        self.display_connected_banner()

    def receive_message(self) -> tuple:
        username_header = self.socket.recv(HEADER_LENGTH)

        if not len(username_header):
            self.logger.error("Server has closed the connection.")
            sys.exit(1)

        username_len = int(username_header.decode().strip())
        username = self.socket.recv(username_len).decode()

        msg_length = int(self.socket.recv(HEADER_LENGTH).decode().strip())
        msg = self.socket.recv(msg_length).decode()

        return username, msg

    def send_message(self, message: t.Optional[str] = None) -> None:
        if message:
            message = message.replace("\n", "").encode()
            message_header = self.get_header(message)

            # Key auth
            key_sign = RSA.sign_message(message, self.PRIVATE_KEY)
            key_sign_header = self.get_header(key_sign)

            self.socket.send(key_sign_header + key_sign)
            self.socket.send(message_header + message)
