from __future__ import annotations

from typing import TYPE_CHECKING

import rsa

from zerocom.packets.abc import Packet
from zerocom.protocol.base_io import BaseReader, BaseWriter

if TYPE_CHECKING:
    from typing_extensions import Self


class MessagePacket(Packet):
    """Packet conveying message information."""

    PACKET_ID = 0

    def __init__(self, content: str, signature: bytes) -> None:
        super().__init__()
        self.content = content
        self.signature = signature

    def write(self, writer: BaseWriter) -> None:
        writer.write_bytearray(self.signature)
        writer.write_utf(self.content)

    @classmethod
    def read(cls, reader: BaseReader) -> Self:
        signature = reader.read_bytearray()
        content = reader.read_utf()
        return cls(content, signature)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content={self.content!r}, signature={self.signature!r})"

    def verify(self, public_key: rsa.PublicKey) -> bool:
        """Verify that the message signature was made by a private key with given public_key."""
        try:
            used_hash = rsa.verify(self.content.encode(), self.signature, public_key)
        except rsa.VerificationError:
            return False
        else:
            return used_hash == "SHA-1"

    @classmethod
    def make_signed(cls, content: str, private_key: rsa.PrivateKey) -> Self:
        """Create a new message packet with given content signed by given private_key."""
        signature = rsa.sign(content.encode(), private_key, "SHA-1")
        return cls(content, signature)
