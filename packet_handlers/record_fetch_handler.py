from db_client.handler import *

class RecordFetchHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        result = self.packet.data["result"]
        record_time = self.packet.data["record_time"]
        self.notify_sub_handlers(result, record_time)
