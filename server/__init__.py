import os
import socket
import sys
import threading
import time
import typing as t

import rsa
from utils.config import HEADER_LENGTH, MOTD
from utils.logger import Logger
from utils.utils import get_color, on_startup

logger = Logger()


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
        self, sock: socket.socket, address: list, uname: dict, pub_key: dict
    ) -> None:
        self.socket = sock

        self.ip, self.port = address
        self.address = f"{address[0]}:{address[1]}"

        self.username_header = uname["header"]
        self.raw_username = uname["data"]
        self.username = self.raw_username.decode()

        if pub_key:
            self.pub_key_header = pub_key["header"]
            self.pub_key_pem = pub_key["data"]
            self.pub_key = rsa.PublicKey.load_pkcs1(self.pub_key_pem)

    @staticmethod
    def get_header(message: str) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode()


class Server(threading.Thread):
    __slots__ = (
        "socket_list",
        "clients",
        "host",
        "port",
        "socket",
        "start_timer",
        "startup_duration",
        "backlog",
    )

    def __init__(self, address: tuple, backlog: t.Optional[int] = None) -> None:
        super().__init__()

        self.sockets_list = []
        self.clients = {}

        self.host, self.port = address

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name == "posix":
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )  # REUSE_ADDR works diff on windows.

        self.start_timer = time.perf_counter()
        self.startup_duration = None

        self.backlog = backlog

        self.motd = MOTD

    def connect(self) -> None:
        try:
            self.socket.bind((self.host, self.port))
        except OSError:
            self.socket.close()

            on_startup("Server")
            logger.error("Server could not be initialized. Check the PORT.")

            sys.exit(1)
        else:
            end = time.perf_counter()
            duration = round((end - self.start_timer) * 1000, 2)

            on_startup("Server", duration, ip=self.host, port=self.port)

            # Listening backlog
            if not self.backlog:
                self.socket.listen()
            else:
                self.socket.listen(int(self.backlog))

            self.socket.setblocking(False)

            self.sockets_list.append(self.socket)

            logger.success("Server started. Listening for connections.")

    def disconnect(self) -> None:
        for socket_ in self.sockets_list:
            socket_.close()

    def remove_errored_sockets(self, errored_sockets: list) -> None:
        for socket_ in errored_sockets:
            client = self.clients[socket_]
            logger.warning(f"{get_color('YELLOW')}Exception occurred. Location {client.username} [{client.address}]")

            self.sockets_list.remove(socket_)
            del self.clients[socket_]

    @staticmethod
    def receive_message(socket_: socket) -> t.Union[dict, bool]:
        try:
            message_header = socket_.recv(HEADER_LENGTH)

            if not len(message_header):
                return False

            message_length = int(message_header.decode().strip())

            return {"header": message_header, "data": socket_.recv(message_length)}
        except Exception:
            return False

    def process_connection(self) -> None:
        socket_, address = self.socket.accept()

        uname = self.receive_message(socket_)
        pub_key = self.receive_message(socket_)

        client = Client(socket_, address, uname, pub_key)

        if not uname:
            logger.error(f"New connection failed from {client.address}.")
        elif not pub_key:
            logger.error(f"New connection failed from {client.address}. No key auth found. {pub_key}")
        else:
            self.sockets_list.append(socket_)
            self.clients[socket_] = client

            # ----- Send the data to Client ---- #
            motd = self.motd.encode()
            motd_header = client.get_header(motd)

            client.socket.send(motd_header + motd)

            # ---------------------------------- #

            logger.success(
                f"{get_color('GREEN')}Accepted new connection requested by {client.username} [{client.address}]."
            )

    def process_message(self, socket_: socket) -> bool:
        def broadcast(message: dict) -> None:
            for client_socket in self.clients:
                if client_socket != socket_:
                    sender_information = client.username_header + client.raw_username
                    message_to_send = message["header"] + message["data"]

                    client_socket.send(sender_information + message_to_send)

        sign = self.receive_message(socket_)
        message = self.receive_message(socket_)

        if not message or not sign:
            client = self.clients[socket_]

            logger.error(f"Connection closed [{client.username}@{client.address}]")

            self.sockets_list.remove(socket_)
            del self.clients[socket_]

            return False

        client = self.clients[socket_]

        try:
            if rsa.verify(message["data"], sign["data"], client.pub_key):
                msg = message["data"].decode()

                logger.message(client.username, msg)
                broadcast(message)
        except rsa.pkcs1.VerificationError:
            logger.warning(
                f"Received incorrect verification from {client.address} [{client.username}] | "
                f"message:{message['data'].decode()})"
            )

            warning = {
                "data": "Messaging failed from user due to incorrect verification.".encode()
            }
            warning["header"] = client.get_header(warning["data"])
            broadcast(warning)

            return False
