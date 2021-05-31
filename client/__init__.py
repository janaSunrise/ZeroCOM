import socket
import sys
import time
import typing as t

import rsa
from utils.config import HEADER_LENGTH
from utils.logger import Logger
from utils.utils import on_startup

logger = Logger()


class Client:
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
        self.host = address[0]
        self.port = address[1]
        self.username = username

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.start_timer = time.perf_counter()
        self.startup_duration = None

        self.PUBLIC_KEY, self.PRIVATE_KEY = rsa.newkeys(512)

        self.motd = None

    @staticmethod
    def get_header(message: bytes) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode()

    def connect(self) -> None:
        try:
            self.socket.connect((self.host, self.port))
        except ConnectionRefusedError:
            on_startup("Client")
            logger.error("Connection could not be established. Invalid HOST/PORT.")
            sys.exit(1)
        else:
            end = time.perf_counter()
            self.startup_duration = round((end - self.start_timer) * 1000, 2)

            # Initialize the connection, If connected
            self.initialize()

            on_startup("Client", self.startup_duration, motd=self.motd)

            logger.success(f"Connected to remote host at [{self.host}:{self.port}]")

        self.socket.setblocking(False)

    def disconnect(self) -> None:
        self.socket.close()

    def initialize(self) -> None:
        # Send the specified uname.
        uname = self.username.encode()
        uname_header = self.get_header(uname)

        # Key auth
        exported_public_key = rsa.PublicKey.save_pkcs1(self.PUBLIC_KEY, format="PEM")
        public_key_header = self.get_header(exported_public_key)

        # Send the message
        self.socket.send(uname_header + uname)
        self.socket.send(public_key_header + exported_public_key)

        motd_len = int(self.socket.recv(HEADER_LENGTH).decode().strip())
        self.motd = self.socket.recv(motd_len).decode().strip()

    def receive_message(self) -> tuple:
        username_header = self.socket.recv(HEADER_LENGTH)

        if not len(username_header):
            logger.error("Server has closed the connection.")
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
            priv_key_sign = rsa.sign(message, self.PRIVATE_KEY, "SHA-1")
            priv_key_sign_header = self.get_header(priv_key_sign)

            self.socket.send(priv_key_sign_header + priv_key_sign)
            self.socket.send(message_header + message)
