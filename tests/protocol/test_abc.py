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
