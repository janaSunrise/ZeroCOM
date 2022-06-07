from __future__ import annotations

import logging
import os
import socket
from dataclasses import dataclass
from typing import Optional

from zerocom.protocol.connection import SocketConnection

log = logging.getLogger(__name__)


@dataclass(slots=True)
class ProcessedClient:
    conn: SocketConnection
    address: tuple[str, int]
    username: str

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

    def process_connection(self) -> None:
        client_socket, address = self.socket.accept()
        conn = SocketConnection(client_socket)
        log.debug(f"Accepted new connection from {address}")
        try:
            username = conn.read_utf()
        except IOError as exc:
            log.debug(f"Processing new connection from {address} failed when reading username: {exc!r}")
            log.error(f"Dropping connection from {address} - username wasn't send properly when connecting.")
            client_socket.close()
            return

        client = ProcessedClient(conn, address, username)
        self.connected_clients[client_socket] = client

    def process_message(self, client_socket: socket.socket) -> None:
        client = self.connected_clients[client_socket]

        try:
            msg = client.conn.read_utf()
        except IOError as exc:
            log.debug(f"Processing message from {client} failed: {exc}")
            log.error(f"Dropping connection from {client} - sent invalid message")
            client.socket.close()
            del self.connected_clients[client_socket]
            return

        log.info(f"Accepted message from {client}: {msg}")

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
