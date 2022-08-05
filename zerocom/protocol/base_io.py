from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from enum import Enum
from itertools import count
from typing import Literal, TypeAlias, Union, overload

from zerocom.protocol.utils import from_twos_complement, to_twos_complement


class StructFormat(str, Enum):
    """All possible write/read struct types."""

    BOOL = "?"
    CHAR = "c"
    BYTE = "b"
    UBYTE = "B"
    SHORT = "h"
    USHORT = "H"
    INT = "i"
    UINT = "I"
    LONG = "l"
    ULONG = "L"
    FLOAT = "f"
    DOUBLE = "d"
    HALFFLOAT = "e"
    LONGLONG = "q"
    ULONGLONG = "Q"


INT_FORMATS_TYPE: TypeAlias = Union[
    Literal[StructFormat.BYTE],
    Literal[StructFormat.UBYTE],
    Literal[StructFormat.SHORT],
    Literal[StructFormat.USHORT],
    Literal[StructFormat.INT],
    Literal[StructFormat.UINT],
    Literal[StructFormat.LONG],
    Literal[StructFormat.ULONG],
    Literal[StructFormat.LONGLONG],
    Literal[StructFormat.ULONGLONG],
]

FLOAT_FORMATS_TYPE: TypeAlias = Union[
    Literal[StructFormat.FLOAT],
    Literal[StructFormat.DOUBLE],
    Literal[StructFormat.HALFFLOAT],
]


class BaseWriter(ABC):
    """Base class holding write buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def write(self, data: bytes) -> None:
        ...

    @overload
    def write_value(self, fmt: INT_FORMATS_TYPE, value: int) -> None:
        ...

    @overload
    def write_value(self, fmt: FLOAT_FORMATS_TYPE, value: float) -> None:
        ...

    @overload
    def write_value(self, fmt: Literal[StructFormat.BOOL], value: bool) -> None:
        ...

    @overload
    def write_value(self, fmt: Literal[StructFormat.CHAR], value: str) -> None:
        ...

    def write_value(self, fmt: StructFormat, value: object) -> None:
        """Write a value of given struct format in big-endian mode."""
        try:
            self.write(struct.pack(">" + fmt.value, value))
        except struct.error as exc:
            raise ValueError(str(exc)) from exc

    def write_varuint(self, value: int, /, *, max_bits: int) -> None:
        """Write an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Writing will be limited up to integer values of `max_bits` bits, and trying to write bigger values will rase a
        ValueError. Note that setting `max_bits` to for example 32 bits doesn't mean that at most 4 bytes will be sent,
        in this case it would actually take at most 5 bytes, due to the variable encoding overhead.

        Varints send bytes where 7 least significant bits are value bits, and the most significant bit is continuation
        flag bit. If this continuation bit is set (1), it indicates that there will be another varnum byte sent after
        this one. The least significant group is written first, followed by each of the more significant groups, making
        varnums little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_bits)) - 1
        if value < 0 or value > value_max:
            raise ValueError(f"Tried to write varint outside of the range of {max_bits}-bit int.")

        remaining = value
        while True:
            if remaining & ~0x7F == 0:  # final byte
                self.write_value(StructFormat.UBYTE, remaining)
                return
            # Write only 7 least significant bits with the first bit being 1, marking there will be another byte
            self.write_value(StructFormat.UBYTE, remaining & 0x7F | 0x80)
            # Subtract the value we've already sent (7 least significant bits)
            remaining >>= 7

    def write_varint(self, value: int, /, *, max_bits: int) -> None:
        """Write an arbitrarily big signed integer in a variable length format.

        For more information about varints check `write_varuint` docstring.
        """
        val = to_twos_complement(value, bits=max_bits)
        self.write_varuint(val, max_bits=max_bits)

    def write_utf(self, value: str, /, *, max_varuint_bits: int = 16) -> None:
        """Write a UTF-8 encoded string, prefixed with a varuint of given bit size.

        Will write n bytes, depending on the amount of bytes in the string + bytes from prefix varuint,
        holding this size (n).

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. In most
        cases, characters will generally only take 1 byte per character (for all ASCII characters).

        The amount of bytes can't surpass the specified varuint size, otherwise a ValueError will be raised from trying
        to write an invalid varuint.
        """
        data = bytearray(value, "utf-8")
        self.write_varuint(len(data), max_bits=max_varuint_bits)
        self.write(data)

    def write_bytearray(self, data: bytearray, /, *, max_varuint_bits: int = 16) -> None:
        """Write an arbitrary sequence of bytes, prefixed with a varint of it's size."""
        self.write_varuint(len(data), max_bits=max_varuint_bits)
        self.write(data)


class BaseReader(ABC):
    """Base class holding read buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def read(self, length: int) -> bytearray:
        ...

    @overload
    def read_value(self, fmt: INT_FORMATS_TYPE) -> int:
        ...

    @overload
    def read_value(self, fmt: FLOAT_FORMATS_TYPE) -> float:
        ...

    @overload
    def read_value(self, fmt: Literal[StructFormat.BOOL]) -> bool:
        ...

    @overload
    def read_value(self, fmt: Literal[StructFormat.CHAR]) -> str:
        ...

    def read_value(self, fmt: StructFormat) -> object:
        """Read a value into given struct format in big-endian mode.

        The amount of bytes to read will be determined based on the struct format automatically.
        """
        length = struct.calcsize(fmt.value)
        data = self.read(length)
        try:
            unpacked = struct.unpack(">" + fmt.value, data)
        except struct.error as exc:
            raise ValueError(str(exc)) from exc
        return unpacked[0]

    def read_varuint(self, *, max_bits: int) -> int:
        """Read an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Reading will be limited up to integer values of `max_bits` bits, and trying to read bigger values will rase an
        IOError. Note that setting `max_bits` to for example 32 bits doesn't mean that at most 4 bytes will be read,
        in this case it would actually read at most 5 bytes, due to the variable encoding overhead.

        Varints send bytes where 7 least significant bits are value bits, and the most significant bit is continuation
        flag bit. If this continuation bit is set (1), it indicates that there will be another varnum byte sent after
        this one. The least significant group is written first, followed by each of the more significant groups, making
        varnums little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_bits)) - 1

        result = 0
        for i in count():  # pragma: no branch # count() iterator won't ever deplete
            byte = self.read_value(StructFormat.UBYTE)
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if result > value_max:
                raise IOError(f"Received varint was outside the range of {max_bits}-bit int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result

    def read_varint(self, *, max_bits: int) -> int:
        """Read an arbitrarily big signed integer in a variable length format.

        For more information about varints check `read_varuint` docstring.
        """
        unsigned_num = self.read_varuint(max_bits=max_bits)
        val = from_twos_complement(unsigned_num, bits=max_bits)
        return val

    def read_utf(self, *, max_varuint_bits: int = 16) -> str:
        """Read a UTF-8 encoded string, prefixed with a varuint of given bit size.

        Will read n bytes, depending on the amount of bytes in the string + bytes from prefix varuint,
        holding this size (n)

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. In most
        cases, characters will generally only take 1 byte per character (for all ASCII characters).

        The amount of bytes can't surpass the specified varuint size, otherwise an IOError will be raised from trying
        to read an invalid varuint.
        """
        length = self.read_varuint(max_bits=max_varuint_bits)
        bytes = self.read(length)
        return bytes.decode("utf-8")

    def read_bytearray(self, *, max_varuint_bits: int = 16) -> bytearray:
        """Read an arbitrary sequence of bytes, prefixed with a varint of it's size."""
        length = self.read_varuint(max_bits=max_varuint_bits)
        return self.read(length)
