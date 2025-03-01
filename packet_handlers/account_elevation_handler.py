from db_client.handler import *

class AccountElevationHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        result = self.packet.data["result"]
        self.notify_sub_handlers(result)