from collections.abc import Callable
from db_client.packet import BasePacket
import socket


class BaseHandler:
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        self.client_socket = client_socket
        self.packet = packet
        self.sub_handlers: list[Callable] = []

    def handle(self):
        pass

    def notify_sub_handlers(self, *args, **kwargs):
        if not self.sub_handlers:
            return
        for func in self.sub_handlers:
            func(*args, **kwargs)

    def add_sub_handler(self, func: Callable):
        self.sub_handlers.append(func)
