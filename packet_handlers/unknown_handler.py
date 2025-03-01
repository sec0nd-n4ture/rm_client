from db_client.handler import *

class UnknownHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        print("Unknown packet received.")
