from __future__ import annotations

from abc import ABC
from typing import ClassVar

from zerocom.protocol.rw_capable import ReadWriteCapable


class Packet(ReadWriteCapable, ABC):
    """Base class for all packets"""

    PACKET_ID: ClassVar[int]

    def __init__(self, *args, **kwargs):
        """Enforce PAKCET_ID being set for each instance of concrete packet classes."""
        cls = self.__class__
        if not hasattr(cls, "PACKET_ID"):
            raise TypeError(f"Can't instantiate abstract {cls.__name__} class without defining PACKET_ID variable.")
        return super().__init__(*args, **kwargs)
