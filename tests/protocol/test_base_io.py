from __future__ import annotations

from typing import Any

import pytest

from tests.protocol.helpers import ReadFunctionMock, Reader, WriteFunctionMock, Writer
from zerocom.protocol.base_io import INT_FORMATS_TYPE, StructFormat
from zerocom.protocol.utils import to_twos_complement


class TestReader:
    @classmethod
    def setup_class(cls):
        """Initialize writer instance to be tested."""
        cls.reader = Reader()

    @pytest.fixture
    def read_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Monkeypatch the read function with a mock which is returned."""
        mock_f = ReadFunctionMock()
        monkeypatch.setattr(self.reader.__class__, "read", mock_f)
        yield mock_f

        # Run this assertion after the test, to ensure that all specified data
        # to be read, actually was read
        mock_f.assert_read_everything()

    @pytest.mark.parametrize(
        "format,read_bytes,expected_value",
        (
            (StructFormat.UBYTE, [0], 0),
            (StructFormat.UBYTE, [10], 10),
            (StructFormat.UBYTE, [255], 255),
            (StructFormat.BYTE, [0], 0),
            (StructFormat.BYTE, [20], 20),
            (StructFormat.BYTE, [127], 127),
            (StructFormat.BYTE, [to_twos_complement(-20, bits=8)], -20),
            (StructFormat.BYTE, [to_twos_complement(-128, bits=8)], -128),
        ),
    )
    def test_read_value(
        self,
        format: INT_FORMATS_TYPE,
        read_bytes: list[int],
        expected_value: Any,
        read_mock: ReadFunctionMock,
    ):
        """Reading given values of certain struct format should produce proper expected values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_value(format) == expected_value

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([0], 0),
            ([1], 1),
            ([2], 2),
            ([15], 15),
            ([127], 127),
            ([128, 1], 128),
            ([129, 1], 129),
            ([255, 1], 255),
            ([192, 132, 61], 1000000),
            ([255, 255, 255, 255, 7], 2147483647),
        ),
    )
    def test_read_varuint(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Reading varuint bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_varint(max_bits=32) == expected_value

    @pytest.mark.parametrize(
        "read_bytes,max_bits",
        (
            ([128, 128, 4], 16),
            ([128, 128, 128, 128, 16], 32),
        ),
    )
    def test_read_varuint_out_of_range(self, read_bytes: list[int], max_bits: int, read_mock: ReadFunctionMock):
        """Varuint reading limited to n max bits should raise an IOError for numbers out of this range."""
        read_mock.combined_data = bytearray(read_bytes)
        with pytest.raises(IOError):
            self.reader.read_varuint(max_bits=max_bits)

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([0], 0),
            ([1], 1),
            ([128, 1], 128),
            ([255, 1], 255),
            ([255, 255, 255, 255, 7], 2147483647),
            ([255, 255, 255, 255, 15], -1),
            ([128, 254, 255, 255, 15], -256),
        ),
    )
    def test_read_varint(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Reading varint bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_varint(max_bits=32) == expected_value

    @pytest.mark.parametrize(
        "read_bytes,max_bits",
        (
            ([128, 128, 4], 16),
            ([255, 255, 255, 255, 23], 32),
            ([128, 128, 192, 152, 214, 197, 215, 227, 235, 10], 64),
            ([128, 128, 192, 231, 169, 186, 168, 156, 148, 245, 255, 255, 255, 255, 3], 64),
        ),
    )
    def test_read_varint_out_of_range(self, read_bytes: list[int], max_bits: int, read_mock: ReadFunctionMock):
        """Reading varint outside of signed max_bits int range should raise ValueError on it's own."""
        read_mock.combined_data = bytearray(read_bytes)
        with pytest.raises(IOError):
            self.reader.read_varint(max_bits=max_bits)

        # The data bytearray was intentionally not fully read/depleted, however by default
        # ending the function with data remaining in the read_mock would trigger an
        # AssertionError, so we expllicitly clear it here to prevent that error
        read_mock.combined_data = bytearray()

    @pytest.mark.parametrize(
        "read_bytes,expected_string",
        (
            ([len("test")] + list(map(ord, "test")), "test"),
            ([len("a" * 100)] + list(map(ord, "a" * 100)), "a" * 100),
            ([0], ""),
        ),
    )
    def test_read_utf(self, read_bytes: list[int], expected_string: str, read_mock: ReadFunctionMock):
        """Reading UTF string results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_utf() == expected_string

    @pytest.mark.parametrize(
        "read_bytes,expected_bytes",
        (
            ([1, 1], [1]),
            ([0], []),
            ([5, 104, 101, 108, 108, 111], [104, 101, 108, 108, 111]),
        ),
    )
    def test_read_bytearray(self, read_bytes: list[int], expected_bytes: list[int], read_mock: ReadFunctionMock):
        """Writing a bytearray results in correct bytes."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_bytearray() == bytearray(expected_bytes)


class TestWriter:
    @classmethod
    def setup_class(cls):
        """Initialize writer instance to be tested."""
        cls.writer = Writer()

    @pytest.fixture
    def write_mock(self, monkeypatch: pytest.MonkeyPatch):
        """Monkeypatch the write function with a mock which is returned."""
        mock_f = WriteFunctionMock()
        monkeypatch.setattr(self.writer.__class__, "write", mock_f)
        return mock_f

    @pytest.mark.parametrize(
        "format,value,expected_bytes",
        (
            (StructFormat.UBYTE, 0, [0]),
            (StructFormat.UBYTE, 15, [15]),
            (StructFormat.UBYTE, 255, [255]),
            (StructFormat.BYTE, 0, [0]),
            (StructFormat.BYTE, 15, [15]),
            (StructFormat.BYTE, 127, [127]),
            (StructFormat.BYTE, -20, [to_twos_complement(-20, bits=8)]),
            (StructFormat.BYTE, -128, [to_twos_complement(-128, bits=8)]),
        ),
    )
    def test_write_value(
        self,
        format: INT_FORMATS_TYPE,
        value: Any,
        expected_bytes: list[int],
        write_mock: WriteFunctionMock,
    ):
        """Writing different values of certain struct format should produce proper expected values."""
        self.writer.write_value(format, value)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        "format,value",
        (
            (StructFormat.UBYTE, -1),
            (StructFormat.UBYTE, 256),
            (StructFormat.BYTE, -129),
            (StructFormat.BYTE, 128),
        ),
    )
    def test_write_value_out_of_range(
        self,
        format: INT_FORMATS_TYPE,
        value: Any,
    ):
        """Trying to write out of range values for given struct type should produce an exception."""
        with pytest.raises(ValueError):
            self.writer.write_value(format, value)

    @pytest.mark.parametrize(
        "number,expected_bytes",
        (
            (0, [0]),
            (1, [1]),
            (2, [2]),
            (15, [15]),
            (127, [127]),
            (128, [128, 1]),
            (129, [129, 1]),
            (255, [255, 1]),
            (1000000, [192, 132, 61]),
            (2147483647, [255, 255, 255, 255, 7]),
        ),
    )
    def test_write_varuint(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Writing varuints results in correct bytes."""
        self.writer.write_varuint(number, max_bits=32)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        "write_value,max_bits",
        (
            (-1, 128),
            (-1, 1),
            (2**16, 16),
            (2**32, 32),
        ),
    )
    def test_write_varuint_out_of_range(self, write_value: int, max_bits: int):
        """Trying to write a varuint bigger than specified bit size should produce ValueError"""
        with pytest.raises(ValueError):
            self.writer.write_varuint(write_value, max_bits=max_bits)

    @pytest.mark.parametrize(
        "number,expected_bytes",
        (
            (0, [0]),
            (1, [1]),
            (128, [128, 1]),
            (255, [255, 1]),
            (2147483647, [255, 255, 255, 255, 7]),
            (-1, [255, 255, 255, 255, 15]),
            (-256, [128, 254, 255, 255, 15]),
        ),
    )
    def test_write_varint(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Writing varints results in correct bytes."""
        self.writer.write_varint(number, max_bits=32)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        "value,max_bits",
        (
            (-2147483649, 32),
            (2147483648, 32),
            (10**20, 32),
            (-(10**20), 32),
        ),
    )
    def test_write_varint_out_of_range(self, value: int, max_bits: int):
        """Writing varint outside of signed max_bits int range should raise ValueError on it's own."""
        with pytest.raises(ValueError):
            self.writer.write_varint(value, max_bits=max_bits)

    @pytest.mark.parametrize(
        "string,expected_bytes",
        (
            ("test", [len("test")] + list(map(ord, "test"))),
            ("a" * 100, [len("a" * 100)] + list(map(ord, "a" * 100))),
            ("", [0]),
        ),
    )
    def test_write_utf(self, string: str, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Writing UTF string results in correct bytes."""
        self.writer.write_utf(string)
        write_mock.assert_has_data(bytearray(expected_bytes))

    @pytest.mark.parametrize(
        "input_bytes,expected_bytes",
        (
            ([1], [1, 1]),
            ([], [0]),
            ([104, 101, 108, 108, 111], [5, 104, 101, 108, 108, 111]),
        ),
    )
    def test_write_bytearray(self, input_bytes: list[int], expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Writing a bytearray results in correct bytes."""
        self.writer.write_bytearray(bytearray(input_bytes))
        write_mock.assert_has_data(bytearray(expected_bytes))
