import os
import socket
import sys
import threading
import time
import typing as t

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from utils.config import HEADER_LENGTH
from utils.logger import get_logging, get_message_logging
from utils.utils import get_color, on_startup


class Client:
    __slots__ = (
        'socket', 'ip', 'port', 'address',
        'username_header', 'raw_username', 'username',
        'pub_key_header', 'pub_key_pem', 'pub_key'
    )

    def __init__(self, sock: socket.socket, address: list, uname: dict, pub_key: dict) -> None:
        self.socket = sock

        self.ip, self.port = address
        self.address = f"{address[0]}:{address[1]}"

        self.username_header = uname["header"]
        self.raw_username = uname["data"]
        self.username = self.raw_username.decode("utf-8")

        if pub_key:
            self.pub_key_header = pub_key["header"]
            self.pub_key_pem = pub_key["data"]
            self.pub_key = RSA.import_key(self.pub_key_pem)

    @staticmethod
    def get_header(message: str) -> bytes:
        return f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")


class Server(threading.Thread):
    __slots__ = (
        'socket_list', 'clients',
        'host', 'port', 'socket',
        'start_timer', 'startup_duration',
        'backlog'
    )

    def __init__(self, address: tuple, backlog: t.Optional[int] = None) -> None:
        super().__init__()

        self.sockets_list = []
        self.clients = {}

        self.host, self.port = address

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name == "posix":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # REUSE_ADDR works diff on windows.

        self.start_timer = time.perf_counter()
        self.startup_duration = None

        self.backlog = backlog

    def connect(self) -> None:
        try:
            self.socket.bind((self.host, self.port))
        except OSError:
            self.socket.close()

            on_startup("Server")
            print(get_logging("error", "Server could not be initialized. Check the PORT."))

            sys.exit(1)
        else:
            end = time.perf_counter()
            duration = round((end - self.start_timer) * 1000, 2)

            on_startup("Server", duration, ip=self.host, port=self.port)

            # Listening backlog
            if not self.backlog:
                self.socket.listen()
            else:
                self.socket.listen(self.backlog)

            self.sockets_list.append(self.socket)

            print(get_logging("success", "Server started. Listening for connections."))

    def disconnect(self) -> None:
        for socket_ in self.sockets_list:
            socket_.close()

    def remove_errored_sockets(self, errored_sockets: list) -> None:
        for socket_ in errored_sockets:
            client = self.clients[socket_]
            print(
                get_logging(
                    "warning",
                    f"{get_color('YELLOW')}Exception occurred. Location {client.username} [{client.address}]"
                )
            )

            self.sockets_list.remove(socket_)
            del self.clients[socket_]

    @staticmethod
    def receive_message(socket_) -> t.Union[dict, bool]:
        try:
            message_header = socket_.recv(HEADER_LENGTH)

            if not len(message_header):
                return False

            message_length = int(message_header.decode("utf-8").strip())

            return {"header": message_header, "data": socket_.recv(message_length)}
        except Exception:
            return False

    def process_connection(self) -> None:
        socket_, address = self.socket.accept()

        uname = self.receive_message(socket_)
        pub_key = self.receive_message(socket_)

        client = Client(socket_, address, uname, pub_key)

        if not uname:
            print(get_logging("error", f"New connection failed from {client.address}."))
        elif not pub_key:
            print(get_logging("error", f"New connection failed from {client.address}. No key auth found."))
        else:
            self.sockets_list.append(socket_)
            self.clients[socket_] = client

            print(get_logging(
                "success",
                f"{get_color('GREEN')}Accepted new connection requested by {client.username} [{client.address}]."
            ))

    def process_message(self, socket_) -> bool:
        def broadcast(msg: dict) -> None:
            for client_socket in self.clients:
                if client_socket != socket_:
                    sender_information = client.username_header + client.raw_username
                    message_to_send = msg["header"] + msg["data"]

                    client_socket.send(sender_information + message_to_send)

        message = self.receive_message(socket_)
        sign = self.receive_message(socket_)

        if not message or not sign:
            client = self.clients[socket_]

            print(get_logging("error", f"Connection closed [{client.username}@{client.address}]."))

            self.sockets_list.remove(socket_)
            del self.clients[socket_]

            return False

        client = self.clients[socket_]

        try:
            signer = PKCS1_v1_5.new(client.pub_key)

            digest = SHA256.new()
            digest.update(message["data"])

            if signer.verify(digest, sign["data"]):
                msg = message['data'].decode('utf-8')

                print(get_message_logging(client.username, msg))
                broadcast(message)
        except Exception:
            print(get_logging(
                "warning", f'Received incorrect verification from {client.address} [{client.username}] | '
                           f'message:{message["data"].decode("utf-8")})'
            ))

            warning = {
                "data": "Messaging failed from user due to incorrect verification.".encode("utf-8")
            }
            warning["header"] = client.get_header(warning["data"])
            broadcast(warning)
            return False
