from __future__ import annotations

import socket
from typing import TYPE_CHECKING

from app.protocol.abc import BaseReader, BaseWriter

if TYPE_CHECKING:
    from typing_extensions import Self


class SocketConnection(BaseReader, BaseWriter):
    def __init__(self, socket: socket.socket):
        self.socket = socket

    @classmethod
    def from_address(cls, address: tuple[str, int], timeout: float) -> Self:
        sock = socket.create_connection(address, timeout=timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        return cls(sock)

    def read(self, length: int) -> bytearray:
        result = bytearray()
        while len(result) < length:
            new = self.socket.recv(length - len(result))
            if len(new) == 0:
                if len(result) == 0:
                    raise IOError("Server did not respond with any information.")
                raise IOError(f"Server stopped responding (got {len(result)} bytes, but expected {length} bytes).")
            result.extend(new)

        return result

    def write(self, data: bytes) -> None:
        self.socket.send(data)

    def __del__(self):
        self.socket.close()
