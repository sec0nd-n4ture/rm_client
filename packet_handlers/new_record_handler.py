from db_client.handler import *

class NewRecordHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        self.notify_sub_handlers(
            self.packet.data["replay_id"], 
            self.packet.data["record_time"], 
            self.packet.data["route_id"]
        )
