from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from itertools import count
from typing import Any, Optional, cast

from zerocom.protocol.utils import enforce_range


class BaseWriter(ABC):
    """Base class holding write buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def write(self, data: bytes) -> None:
        ...

    def _write_packed(self, fmt: str, *value: object) -> None:
        """Write a value of given struct format in big-endian mode.

        Available formats are listed in struct module's docstring.
        """
        self.write(struct.pack(">" + fmt, *value))

    @enforce_range(typ="Byte (8-bit signed int)", byte_size=1, signed=True)
    def write_byte(self, value: int) -> None:
        """Write a single signed 8-bit integer.

        Signed 8-bit integers must be within the range of -128 and 127. Going outside this range will raise a
        ValueError.

        Number is written in two's complement format.
        """
        self._write_packed("b", value)

    @enforce_range(typ="Unsigned byte (8-bit unsigned int)", byte_size=1, signed=False)
    def write_ubyte(self, value: int) -> None:
        """Write a single unsigned 8-bit integer.

        Unsigned 8-bit integers must be within range of 0 and 255. Going outside this range will raise a ValueError.
        """
        self._write_packed("B", value)

    def write_varint(self, value: int, *, max_size: Optional[int] = None) -> None:
        """Write an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Will keep writing bytes until the value is depleted (fully sent). If `max_size` is specified, writing will be
        limited up to integer values of max_size bytes, and trying to write bigger values will rase a ValueError. Note
        that limiting to max_size of 4 (32-bit int) doesn't imply at most 4 bytes will be sent, and will in fact take 5
        bytes at most, due to the variable encoding overhead.

        Varnums use 7 least significant bits of each sent byte to encode the value, and the most significant bit to
        indicate whether there is another byte after it. The least significant group is written first, followed by each
        of the more significant groups, making varints little-endian, however in groups of 7 bits, not 8.
        """
        # We can't use enforce_range as decorator directly, because our byte_size varies
        # instead run it manually from here as a check function
        _wrapper = enforce_range(
            typ=f"{max_size if max_size else 'unlimited'}-byte unsigned varnum",
            byte_size=max_size if max_size else None,
            signed=False,
        )
        _check_f = _wrapper(lambda self, value: None)
        _check_f(self, value)

        remaining = value
        while True:
            if remaining & ~0x7F == 0:  # final byte
                self.write_ubyte(remaining)
                return
            # Write only 7 least significant bits, with the first being 1.
            # first bit here represents that there will be another value after
            self.write_ubyte(remaining & 0x7F | 0x80)
            # Subtract the value we've already sent (7 least significant bits)
            remaining >>= 7

    def write_utf(self, value: str, max_varint_size: int = 2) -> None:
        """Write a UTF-8 encoded string, prefixed with a varshort of it's size (in bytes).

        Will write n bytes, depending on the amount of bytes in the string + up to 3 bytes from prefix varshort,
        holding this size (n). This means a maximum of 2**31-1 + 5 bytes can be written.

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 8192 characters can be written, however this number
        will usually be much bigger (up to 4x) since it's unlikely each character would actually take up 4 bytes. (All
        of the ASCII characters only take up 1 byte).

        If the given string is longer than this, ValueError will be raised for trying to write an invalid varshort.
        """
        data = bytearray(value, "utf-8")
        self.write_varint(len(value), max_size=max_varint_size)
        self.write(data)


class BaseReader(ABC):
    """Base class holding read buffer/connection interactions."""

    __slots__ = ()

    @abstractmethod
    def read(self, length: int) -> bytearray:
        ...

    def _read_unpacked(self, fmt: str) -> Any:  # noqa: ANN401
        """Read bytes and unpack them into given struct format in big-endian mode.


        The amount of bytes to read will be determined based on the format string automatically.
        i.e.: With format of "iii" (referring to 3 signed 32-bit ints), the read length is set as 3x4 (since a signed
            32-bit int takes 4 bytes), making the total length to read 12 bytes, returned as Tuple[int, int, int]

        Available formats are listed in struct module's docstring.
        """
        length = struct.calcsize(fmt)
        data = self.read(length)
        unpacked = struct.unpack(">" + fmt, data)

        if len(unpacked) == 1:
            return unpacked[0]
        return unpacked

    def read_byte(self) -> int:
        """Read a single signed 8-bit integer.

        Will read 1 byte in two's complement format, getting int values between -128 and 127.
        """
        return self._read_unpacked("b")

    def read_ubyte(self) -> int:
        """Read a single unsigned 8-bit integer.

        Will read 1 byte, getting int value between 0 and 255 directly.
        """
        return self._read_unpacked("B")

    def read_varint(self, *, max_size: Optional[int] = None) -> int:
        """Read an arbitrarily big unsigned integer in a variable length format.

        This is a standard way of transmitting ints, and it allows smaller numbers to take less bytes.

        Will keep reading bytes until the value is depleted (fully sent). If `max_size` is specified, reading will be
        limited up to integer values of max_size bytes, and trying to read bigger values will rase an IOError. Note
        that limiting to max_size of 4 (32-bit int) doesn't imply at most 4 bytes will be sent, and will in fact take 5
        bytes at most, due to the variable encoding overhead.

        Varnums use 7 least significant bits of each sent byte to encode the value, and the most significant bit to
        indicate whether there is another byte after it. The least significant group is written first, followed by each
        of the more significant groups, making varints little-endian, however in groups of 7 bits, not 8.
        """
        value_max = (1 << (max_size * 8)) - 1 if max_size else None
        result = 0
        for i in count():
            byte = self.read_ubyte()
            # Read 7 least significant value bits in this byte, and shift them appropriately to be in the right place
            # then simply add them (OR) as additional 7 most significant bits in our result
            result |= (byte & 0x7F) << (7 * i)

            # Ensure that we stop reading and raise an error if the size gets over the maximum
            # (if the current amount of bits is higher than allowed size in bits)
            if value_max and result > value_max:
                max_size = cast(int, max_size)
                raise IOError(f"Received varint was outside the range of {max_size}-byte ({max_size * 8}-bit) int.")

            # If the most significant bit is 0, we should stop reading
            if not byte & 0x80:
                break

        return result

    def read_utf(self, max_varint_size: int = 2) -> str:
        """Read a UTF-8 encoded string, prefixed with a varshort of it's size (in bytes).

        Will read n bytes, depending on the prefix varint (amount of bytes in the string) + up to 3 bytes from prefix
        varshort itself, holding this size (n). This means a maximum of 2**15-1 + 3 bytes can be read (and written).

        Individual UTF-8 characters can take up to 4 bytes, however most of the common ones take up less. Assuming the
        worst case of 4 bytes per every character, at most 8192 characters can be written, however this number
        will usually be much bigger (up to 4x) since it's unlikely each character would actually take up 4 bytes. (All
        of the ASCII characters only take up 1 byte).
        """
        length = self.read_varint(max_size=max_varint_size)
        bytes = self.read(length)
        return bytes.decode("utf-8")
