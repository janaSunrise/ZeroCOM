import os
import socket
import sys
import time
import typing as t

import rsa

from .message import Message
from .server_side_client import Client
from ..config import HEADER_LENGTH, MOTD
from ..mixins.logging import CustomLoggingClass
from ..utils import get_color, on_startup


class Server(CustomLoggingClass):
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
            # REUSE_ADDR works differently on windows
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
            self.logger.error(f"Server could not be initialized. Error: {exc}")

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

            self.logger.success("Server started. Listening for connections.")

    def disconnect(self) -> None:
        for socket_ in self.sockets_list:
            socket_.close()

    def remove_specified_socket(self, sock: socket.socket) -> None:
        self.sockets_list.remove(sock)
        del self.clients[sock]

    def remove_errored_sockets(self, errored_sockets: list) -> None:
        for socket_ in errored_sockets:
            client = self.clients[socket_]
            self.logger.warning(
                f"{get_color('YELLOW')}Exception occurred. Location: {client.username} [{client.address}]"
            )

            self.remove_specified_socket(socket_)

    def receive_message(self, socket_: socket) -> t.Optional[Message]:
        try:
            message_header = socket_.recv(HEADER_LENGTH)
            if not len(message_header):
                return

            message_length = int(message_header.decode().strip())

            return Message(message_header, socket_.recv(message_length))
        except Exception as exc:
            self.logger.error(f"Exception occurred: {exc}")

    def process_connection(self) -> None:
        socket_, address = self.socket.accept()

        uname = self.receive_message(socket_)
        pub_key = self.receive_message(socket_)

        client = Client(socket_, address, uname, pub_key)

        if not uname:
            self.logger.error(f"New connection failed from {client.address}.")
            return

        if not pub_key:
            self.logger.error(f"New connection failed from {client.address}. No key auth found. {pub_key}")
            return

        self.sockets_list.append(socket_)
        self.clients[socket_] = client

        # Log successful connection
        self.logger.success(
            f"{get_color('GREEN')}Accepted new connection requested by {client.username} [{client.address}]."
        )

        # Send the data to Client
        motd = self.motd.encode()
        motd_header = client.get_header(motd)

        # Sent the MOTD
        client.socket.send(motd_header + motd)

    def broadcast_message(self, sock: socket.socket, client: Client, message: Message) -> None:
        for client_socket in self.clients:
            if client_socket != sock:
                sender_information = client.username_header + client.raw_username
                message_to_send = message.header + message.data

                client_socket.send(sender_information + message_to_send)

    def process_message(self, socket_: socket) -> None:
        # Receive Signature and message
        sign = self.receive_message(socket_)
        message = self.receive_message(socket_)

        # If disconnected
        if not message or not sign:
            client = self.clients[socket_]

            self.logger.error(f"Connection closed [{client.username}@{client.address}]")
            self.remove_specified_socket(socket_)

            return

        # Get the client
        client = self.clients[socket_]

        # Verify key
        try:
            if rsa.verify(message.data, sign.data, client.pub_key):
                msg = message.data.decode()

                self.logger.message(client.username, msg)
                self.broadcast_message(socket_, client, message)
        except rsa.pkcs1.VerificationError:
            self.logger.warning(
                f"Received incorrect verification from {client.address} [{client.username}] | "
                f"message:{message.data.decode()})"
            )

            warning = Message(None, "Messaging failed from user due to incorrect verification.".encode())
            warning.header = client.get_header(warning.data)

            self.broadcast_message(socket_, client, warning)
            return
