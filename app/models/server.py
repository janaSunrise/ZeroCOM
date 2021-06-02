import os
import socket
import sys
import time
import typing as t

import rsa

from .message import Message
from .server_side_client import Client
from ..config import HEADER_LENGTH, MOTD
from ..utils import get_color, on_startup, Logger

logger = Logger()


class Server:
    __slots__ = (
        "sockets_list",
        "clients",
        "host",
        "port",
        "socket",
        "start_timer",
        "startup_duration",
        "backlog",
        "motd"
    )

    def __init__(self, address: tuple, backlog: t.Optional[int] = None) -> None:
        # List of sockets and clients
        self.sockets_list = []
        self.clients = {}

        # Address to run the server on
        self.host, self.port = address

        # Initialize the main sockets.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name == "posix":
            self.socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )  # REUSE_ADDR works diff on windows.

        # Initialize startup timer and calculate duration
        self.start_timer = time.perf_counter()
        self.startup_duration = None

        # Get the backlog (Max number of connections at a time)
        self.backlog = backlog

        # MOTD of the server
        self.motd = MOTD

    def connect(self) -> None:
        try:
            self.socket.bind((self.host, self.port))
        except OSError as exc:
            self.socket.close()

            on_startup("Server")
            logger.error(f"Server could not be initialized. Error: {exc}")

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

            # Set socket to non-blocking
            self.socket.setblocking(False)

            # Add socket to the list of sockets.
            self.sockets_list.append(self.socket)

            logger.success("Server started. Listening for connections.")

    def disconnect(self) -> None:
        for socket_ in self.sockets_list:
            socket_.close()

    def remove_errored_sockets(self, errored_sockets: list) -> None:
        for socket_ in errored_sockets:
            client = self.clients[socket_]
            logger.warning(f"{get_color('YELLOW')}Exception occurred. Location: {client.username} [{client.address}]")

            self.sockets_list.remove(socket_)
            del self.clients[socket_]

    @staticmethod
    def receive_message(socket_: socket) -> t.Optional[Message]:
        try:
            message_header = socket_.recv(HEADER_LENGTH)
            if not len(message_header):
                return

            message_length = int(message_header.decode().strip())

            return Message(message_header, socket_.recv(message_length))
        except Exception:
            return

    def process_connection(self) -> None:
        socket_, address = self.socket.accept()

        uname = self.receive_message(socket_)
        pub_key = self.receive_message(socket_)

        client = Client(socket_, address, uname, pub_key)

        logger.info(pub_key)

        if not uname:
            logger.error(f"New connection failed from {client.address}.")
        elif not pub_key:
            logger.error(f"New connection failed from {client.address}. No key auth found. {pub_key}")
        else:
            self.sockets_list.append(socket_)
            self.clients[socket_] = client

            # Send the data to Client
            motd = self.motd.encode()
            motd_header = client.get_header(motd)

            client.socket.send(motd_header + motd)
            logger.info("Sent!")

            logger.success(
                f"{get_color('GREEN')}Accepted new connection requested by {client.username} [{client.address}]."
            )

    def process_message(self, socket_: socket) -> bool:
        def broadcast(message: Message) -> None:
            for client_socket in self.clients:
                if client_socket != socket_:
                    sender_information = client.username_header + client.raw_username
                    message_to_send = message.header + message.data

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
            if rsa.verify(message.data, sign.data, client.pub_key):
                msg = message.data.decode()

                logger.message(client.username, msg)
                broadcast(message)
        except rsa.pkcs1.VerificationError:
            logger.warning(
                f"Received incorrect verification from {client.address} [{client.username}] | "
                f"message:{message.data.decode()})"
            )

            warning = Message(None, "Messaging failed from user due to incorrect verification.".encode())
            warning.header = client.get_header(warning.data)
            broadcast(warning)

            return False
