from __future__ import annotations

import pytest

from tests.protocol.helpers import ReadFunctionMock, Reader, WriteFunctionMock, Writer


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
        "read_bytes,expected_value",
        (
            ([10], 10),
            ([255], 255),
            ([0], 0),
        ),
    )
    def test_read_ubyte(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Reading byte int should return an integer in a single unsigned byte."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_ubyte() == expected_value

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([236], -20),
            ([128], -128),
            ([20], 20),
            ([127], 127),
        ),
    )
    def test_read_byte(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Negative number bytes should be read from two's complement format."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_byte() == expected_value

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
    def test_read_varint(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Reading varint bytes results in correct values."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_varint() == expected_value

    @pytest.mark.parametrize(
        "read_bytes,expected_value",
        (
            ([0], 0),
            ([154, 1], 154),
            ([255, 255, 3], 2**16 - 1),
        ),
    )
    def test_read_varint_max_size(self, read_bytes: list[int], expected_value: int, read_mock: ReadFunctionMock):
        """Varint reading should be limitable to n max bytes and work with values in range."""
        read_mock.combined_data = bytearray(read_bytes)
        assert self.reader.read_varint(max_size=2) == expected_value

    def test_read_varnum_max_size_out_of_range(self, read_mock: ReadFunctionMock):
        """Varint reading limited to n max bytes should raise an IOError for numbers out of this range."""
        read_mock.combined_data = bytearray([128, 128, 4])
        with pytest.raises(IOError):
            self.reader.read_varint(max_size=2)

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

    def test_write_byte(self, write_mock: WriteFunctionMock):
        """Writing byte int should store an integer in a single byte."""
        self.writer.write_byte(15)
        write_mock.assert_has_data(bytearray([15]))

    def test_write_byte_negative(self, write_mock: WriteFunctionMock):
        """Negative number bytes should be stored in two's complement format."""
        self.writer.write_byte(-20)
        write_mock.assert_has_data(bytearray([236]))

    def test_write_byte_out_of_range(self):
        """Signed bytes should only allow writes from -128 to 127."""
        with pytest.raises(ValueError):
            self.writer.write_byte(-129)
        with pytest.raises(ValueError):
            self.writer.write_byte(128)

    def test_write_ubyte(self, write_mock: WriteFunctionMock):
        """Writing unsigned byte int should store an integer in a single byte."""
        self.writer.write_byte(80)
        write_mock.assert_has_data(bytearray([80]))

    def test_write_ubyte_out_of_range(self):
        """Unsigned bytes should only allow writes from 0 to 255."""
        with pytest.raises(ValueError):
            self.writer.write_ubyte(256)
        with pytest.raises(ValueError):
            self.writer.write_ubyte(-1)

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
    def test_write_varint(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Writing varints results in correct bytes."""
        self.writer.write_varint(number)
        write_mock.assert_has_data(bytearray(expected_bytes))

    def test_write_varint_out_of_range(self):
        """Varint without max size should only work with positive integers."""
        with pytest.raises(ValueError):
            self.writer.write_varint(-1)

    @pytest.mark.parametrize(
        "number,expected_bytes",
        (
            (0, [0]),
            (154, [154, 1]),
            (2**16 - 1, [255, 255, 3]),
        ),
    )
    def test_write_varint_max_size(self, number: int, expected_bytes: list[int], write_mock: WriteFunctionMock):
        """Varints should be limitable to n max bytes and work with values in range."""
        self.writer.write_varint(number, max_size=2)
        write_mock.assert_has_data(bytearray(expected_bytes))

    def test_write_varint_max_size_out_of_range(self):
        """Varints limited to n max bytes should raise ValueErrors for numbers out of this range."""
        with pytest.raises(ValueError):
            self.writer.write_varint(2**16, max_size=2)

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
