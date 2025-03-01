from db_client.handler import *


class AuthHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        result = self.packet.data["result"]
        cookie = self.packet.data["cookie"]
        self.notify_sub_handlers(result, cookie)
