from db_shared_utils.db_shared import DataType
import json


class BasePacket:
    def __init__(
            self, 
            packet_id: bytes, 
            data_type: int | bytes, 
            data: bytes | dict | None
        ):
        self.packet_id = packet_id
        self.data_type = data_type
        self.data = data

    @classmethod
    def from_bytes(cls, packet_data: bytes):
        packet_id = packet_data[0].to_bytes(1, "little")
        data_type = packet_data[1]
        data = None
        if data_type == DataType.JSON.value:
            data = json.loads(packet_data[2:])
        elif data_type == DataType.BLOB.value:
            data = packet_data[2:]
        return cls(packet_id, data_type, data)

    def pack(self) -> bytes:
        data = self.packet_id if isinstance(self.packet_id, bytes) else self.packet_id.to_bytes(1, "little")
        data += self.data_type.to_bytes(1, "little")
        data += b"" if not self.data else self.data
        return len(data).to_bytes(4, "big") + data
