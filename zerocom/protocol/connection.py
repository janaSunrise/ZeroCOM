from __future__ import annotations

import socket

from zerocom.protocol.abc import BaseReader, BaseWriter


class SocketConnection(BaseReader, BaseWriter):
    """Networked implementation for BaseReader and BaseWriter via python's sockets.

    This class holds all basic interactions for writing/reading data (i.e. sending/receiving) data via sockets.
    """

    def __init__(self, socket: socket.socket):
        self.socket = socket

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
