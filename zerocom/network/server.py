from __future__ import annotations

import logging
import os
import socket
from dataclasses import dataclass
from typing import Optional, cast

import rsa
from rsa.key import PublicKey

from zerocom.protocol.connection import SocketConnection

log = logging.getLogger(__name__)


@dataclass
class ProcessedClient:
    __slots__ = ("conn", "address", "username", "public_key")

    conn: SocketConnection
    address: tuple[str, int]

    username: str
    public_key: PublicKey

    @property
    def socket(self) -> socket.socket:
        return self.conn.socket


class Server:
    def __init__(self, address: tuple[str, int], backlog: Optional[int] = None):
        socket = self._make_socket(address, backlog)
        self.connection = SocketConnection(socket)

        self.host, self.port = address
        self.connected_clients: dict[socket.socket, ProcessedClient] = {}

    @property
    def socket(self) -> socket.socket:
        return self.connection.socket

    @property
    def socket_list(self) -> list[socket.socket]:
        """Produce a list of all currently used sockets."""
        sockets = [client.socket for client in self.connected_clients.values()]
        sockets.append(self.socket)
        return sockets

    @staticmethod
    def _make_socket(address: tuple[str, int], backlog: Optional[int] = None) -> socket.socket:
        """Make server socket capable of accepting new connections."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if os.name == "posix":
            # Allow address reuse (fixes errors when using same address after program restarts)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.setblocking(False)

        try:
            sock.bind(address)
        except OSError as exc:
            sock.close()
            log.critical(f"Unable to bind server to {address} (maybe this address is already in use?)")
            raise exc
        else:
            log.info(f"Server bound to {address}")

        # Enable server to accept connections
        if backlog is not None:
            sock.listen(backlog)
        else:
            sock.listen()

        log.info("Listening for connections...")

        return sock

    def process_connection(self) -> None:
        client_socket, address = self.socket.accept()
        conn = SocketConnection(client_socket)
        log.debug(f"Accepted new connection from {address}")
        try:
            username = conn.read_utf()
            public_key = conn.read_utf()
        except IOError as exc:
            log.debug(f"Processing new connection from {address} failed when reading username: {exc!r}")
            log.error(f"Dropping connection from {address} - username wasn't send properly when connecting.")
            client_socket.close()
            return

        client = ProcessedClient(conn, address, username, cast(PublicKey, PublicKey.load_pkcs1(public_key.encode())))
        self.connected_clients[client_socket] = client

    def process_message(self, client_socket: socket.socket) -> None:
        client = self.connected_clients[client_socket]

        try:
            key_sign = client.conn.read_utf()
            msg = client.conn.read_utf()
        except IOError as exc:
            log.debug(f"Processing message from {client} failed: {exc}")
            log.error(f"Dropping connection from {client} - sent invalid message")
            client.socket.close()
            del self.connected_clients[client_socket]
            return

        log.info(f"Accepted message from {client}: {msg}")

        # RSA verification + broadcasting.
        try:
            if rsa.verify(msg.encode(), key_sign.encode(), client.public_key):
                log.info(f"Message from {client} verified")
                self.broadcast(client.socket, msg)
        except rsa.VerificationError:
            log.error(f"Dropping connection from {client} - received incorrect verification")

            # Broadcast a warning to all clients.
            self.broadcast(client_socket, f"{client.username} has been kicked for incorrect verification.")

            # Close the connection.
            client.socket.close()
            del self.connected_clients[client_socket]

    def broadcast(self, client_socket: socket.socket, message: str) -> None:
        for client_sock in self.connected_clients.values():
            if client_sock.socket != client_socket:
                client_sock.conn.write_utf(client_sock.username)
                client_sock.conn.write_utf(message)
