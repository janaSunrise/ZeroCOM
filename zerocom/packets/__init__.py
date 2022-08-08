from __future__ import annotations

from zerocom.exceptions import MalformedPacketError, MalformedPacketState
from zerocom.packets.abc import Packet
from zerocom.packets.message import MessagePacket
from zerocom.protocol.base_io import BaseReader, BaseWriter, StructFormat

_PACKETS: list[type[Packet]] = [MessagePacket]
PACKET_MAP: dict[int, type[Packet]] = {}

for packet_cls in _PACKETS:
    PACKET_MAP[packet_cls.PACKET_ID] = packet_cls


# TODO: Consider adding these functions into BaseWriter/BaseReader


def write_packet(writer: BaseWriter, packet: Packet) -> None:
    """Write given packet."""
    writer.write_value(StructFormat.SHORT, packet.PACKET_ID)
    packet.write(writer)


def read_packet(reader: BaseReader) -> Packet:
    """Read any arbitrary packet based on it's ID."""
    try:
        packet_id = reader.read_value(StructFormat.SHORT)
    except IOError as exc:
        raise MalformedPacketError(MalformedPacketState.MALFORMED_PACKET_ID, ioerror=exc)

    if packet_id not in PACKET_MAP:
        raise MalformedPacketError(MalformedPacketState.UNRECOGNIZED_PACKET_ID, packet_id=packet_id)

    try:
        return PACKET_MAP[packet_id].read(reader)
    except IOError as exc:
        raise MalformedPacketError(MalformedPacketState.MALFORMED_PACKET_BODY, ioerror=exc, packet_id=packet_id)
