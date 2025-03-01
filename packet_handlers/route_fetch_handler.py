from db_shared_utils.db_network_objects import RouteInfo
from db_client.handler import *

class RouteFetchHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        route_list = [RouteInfo.from_dict(route_dict) for route_dict in self.packet.data]
        self.notify_sub_handlers(route_list)
