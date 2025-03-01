from db_shared_utils.db_shared import PacketID
from db_client.handler import BaseHandler
from db_client.packet import BasePacket
from collections.abc import Callable
import socket

'''
Protocol:

Agreed Packet Structure:
|LENGTH|PACKET_ID|DATA_TYPE|DATA|
    4       1        1 

Read 2048 bytes, write to buffer
extract length from buffer, read as much as length from buffer
remove packet from buffer.
Give packet to handler.
repeat

Data types:
JSON 0
BLOB 1
NODA 2
'''


class Client:
    def __init__(self, server_ip: str, server_port: int) -> None:
        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.subhandler_mapping: dict[PacketID, list[Callable]] = {}
        self.handler_mapping: dict[PacketID, type[BaseHandler]] = {}

    def connect(self):
        self.socket.connect((self.server_ip, self.server_port))

    def parse_data(self):
        buffer = b""
        while True:
            try:
                data: bytes = self.socket.recv(2048)
                if not data: # empty only sent when connection is closed
                    print(f"Connection closed.")
                    break

                buffer += data

                while len(buffer) >= 4:
                    packet_length = int.from_bytes(buffer[:4], byteorder='big', signed=False)

                    if packet_length == 0:
                        print("Invalid packet length: 0")
                        break

                    if len(buffer) < 4 + packet_length:
                        break

                    packet = BasePacket.from_bytes(buffer[4:4 + packet_length])
                    packet_id = PacketID._value2member_map_[packet.packet_id[0]]
                    handler_type = self.handler_mapping[packet_id]
                    if handler_type:
                        handler = handler_type(packet, self.socket)
                        if packet_id in self.subhandler_mapping:
                            handler.sub_handlers = self.subhandler_mapping[packet_id]
                        handler.handle()
                    else:
                        print(f"No handler found for packet ID: {packet.packet_id}")
                    buffer = buffer[4 + packet_length:]
            except socket.timeout:
                print(f"Connection timed out.")
                return False
            except ConnectionResetError:
                print(f"Connection lost.")
                return False
            except OSError:
                print(f"Connection closed gracefully.")
                return False


    def register_handler(self, packet_id: PacketID, handler: type[BaseHandler]):
        self.handler_mapping[packet_id] = handler

    def register_subhandler(self, packet_id: PacketID, sub_handler_func: Callable):
        if packet_id not in self.subhandler_mapping:
            self.subhandler_mapping[packet_id] = []
        self.subhandler_mapping[packet_id].append(sub_handler_func)
