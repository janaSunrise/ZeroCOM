from __future__ import annotations

import socket
from typing import Optional
from unittest.mock import MagicMock

from tests.protocol.helpers import ReadFunctionMock, WriteFunctionMock
from zerocom.protocol.connection import SocketConnection


class MockSocket(MagicMock):
    spec_set = socket.socket

    def __init__(self, *args, read_data: Optional[bytearray] = None, **kw) -> None:
        super().__init__(*args, **kw)
        self.recv = ReadFunctionMock(combined_data=read_data)
        self.send = WriteFunctionMock()


def test_read():
    data = bytearray("hello", "utf-8")
    conn = SocketConnection(MockSocket(read_data=data.copy()))

    out = conn.read(5)

    conn.socket.recv.assert_read_everything()
    assert out == data


def test_write():
    data = bytearray("hello", "utf-8")
    conn = SocketConnection(MockSocket())

    conn.write(data)

    conn.socket.send.assert_has_data(data)
