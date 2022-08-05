from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from zerocom.protocol.base_io import BaseReader, BaseWriter

if TYPE_CHECKING:
    from typing_extensions import Self


class WriteCapable(ABC):
    """Base class providing writing capabilities."""

    @abstractmethod
    def write(self, writer: BaseWriter) -> None:
        raise NotImplementedError()


class ReadCapable(ABC):
    """Base class providing reading capabilities."""

    @classmethod
    @abstractmethod
    def read(cls, reader: BaseReader) -> Self:
        raise NotImplementedError()


class ReadWriteCapable(ReadCapable, WriteCapable):
    """Base class providing read and write capabilities."""
