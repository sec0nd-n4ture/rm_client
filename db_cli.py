from db_shared_utils.db_shared import PacketID, DataType, hash_password, ReplayData
from db_shared_utils.db_network_objects import AccountInfo, RecordInfo, AdminInfo
from packet_handlers.account_creation_handler import AccountCreationHandler
from packet_handlers.account_elevation_handler import AccountElevationHandler
from packet_handlers.authentication_handler import AuthHandler
from packet_handlers.new_record_handler import NewRecordHandler
from packet_handlers.record_fetch_handler import RecordFetchHandler
from packet_handlers.record_update_handler import RecordUpdateHandler
from packet_handlers.replay_download_handler import ReplayDownloadHandler
from packet_handlers.record_fetch_handler import RecordFetchHandler
from packet_handlers.route_fetch_handler import RouteFetchHandler
from packet_handlers.top_fetch_handler import TopFetchHandler
from packet_handlers.unknown_handler import UnknownHandler
from db_client.packet import BasePacket
from db_client.client import Client
from threading import Thread, Lock
import hashlib
import json


class DBClient(Thread):
    def __init__(self, server_ip: str, server_port: int) -> None:
        super().__init__(daemon=True)
        self.client = Client(server_ip, server_port)
        self.client.register_handler(PacketID.ACCOUNT_CREATION, AccountCreationHandler)
        self.client.register_handler(PacketID.ACCOUNT_ELEVATION, AccountElevationHandler)
        self.client.register_handler(PacketID.AUTHENTICATION, AuthHandler)
        self.client.register_handler(PacketID.RECORD_FETCH, RecordFetchHandler)
        self.client.register_handler(PacketID.RECORD_UPDATE, RecordUpdateHandler)
        self.client.register_handler(PacketID.REPLAY_UPLOAD, ReplayDownloadHandler)
        self.client.register_handler(PacketID.NOTIFY_NEW_RECORD, NewRecordHandler)
        self.client.register_handler(PacketID.ROUTE_FETCH, RouteFetchHandler)
        self.client.register_handler(PacketID.TOP_PLACEMENT, TopFetchHandler)
        self.client.register_handler(PacketID.UNKNOWN, UnknownHandler)
        self.send_lock = Lock()

    def run(self) -> None:
        self.client.parse_data()

    def connect(self):
        self.client.connect()

    def __send_async(self, packet: BasePacket):
        with self.send_lock:
            self.client.socket.sendall(packet.pack())
        return

    def send(self, packet: BasePacket, is_async: bool):
        if is_async:
            Thread(target=self.__send_async, args=(packet,), daemon=True).start()
            return
        with self.send_lock:
            self.client.socket.sendall(packet.pack())


    def register(self, username: str, password: str, is_async: bool = False) -> None:
        password_hash = hash_password(password, username)
        info = AccountInfo(username, password_hash.hex())
        data = json.dumps(info.to_dict()).encode()
        packet = BasePacket(
            PacketID.ACCOUNT_CREATION.value,
            DataType.JSON.value,
            data
        )
        self.send(packet, is_async)

    def login(self, username: str, password: str, is_async: bool = False) -> None:
        password_hash = hash_password(password, username)
        info = AccountInfo(username, password_hash.hex())
        data = json.dumps(info.to_dict()).encode()
        packet = BasePacket(
            PacketID.AUTHENTICATION.value,
            DataType.JSON.value,
            data
        )
        self.send(packet, is_async)

    def update_record(
            self, 
            record_time: float, 
            route_id: int, 
            pw_hash: bytes, 
            map_name: str, 
            replay_data: ReplayData,
            is_async: bool = False
        ):
        record_info = RecordInfo(record_time, route_id, map_name, pw_hash.hex())
        replay_data.truncate()
        data = replay_data.get_snapshots_len.to_bytes(4, "little")
        data += replay_data.data
        data += json.dumps(record_info.to_dict()).encode()

        packet = BasePacket(
            PacketID.RECORD_UPDATE.value,
            DataType.BLOB.value,
            data
        )
        self.send(packet, is_async)

    def request_routes(self, map_name: str, is_async: bool = False):
        packet = BasePacket(
            PacketID.ROUTE_FETCH.value,
            DataType.JSON.value,
            json.dumps({"map_name": map_name}).encode()
        )
        self.send(packet, is_async)

    def request_top(self, route_id: int, map_name: str, page: int = 0, is_async: bool = False):
        packet = BasePacket(
            PacketID.TOP_PLACEMENT.value,
            DataType.JSON.value,
            json.dumps({
                "route_id": route_id, 
                "page": page, 
                "map_name": map_name
            }).encode()
        )

        self.send(packet, is_async)

    def request_own_record(self, map_name: str, route_id: int, pw_hash: bytes, is_async: bool = False):
        packet = BasePacket(
            PacketID.RECORD_FETCH.value,
            DataType.JSON.value,
            json.dumps({
                "map_name": map_name,
                "route_id": route_id,
                "password_hash": pw_hash.hex()
            }).encode()
        )

        self.send(packet, is_async)

    def request_replay_download(self, replay_id: int, is_async: bool = False):
        packet = BasePacket(
            PacketID.REPLAY_DOWNLOAD.value,
            DataType.JSON.value,
            json.dumps({"replay_id": replay_id}).encode()
        )

        self.send(packet, is_async)

    def elevate_account(self, admin_password: str, cookie: bytes, is_async: bool = False):
        admin_info = AdminInfo(cookie.hex(), hashlib.sha256(admin_password.encode()).hexdigest())
        packet = BasePacket(
            PacketID.ACCOUNT_ELEVATION.value,
            DataType.JSON.value,
            json.dumps(admin_info.to_dict()).encode()
        )

        self.send(packet, is_async)

    def close(self, is_async: bool = False):
        self.send(
            BasePacket(
                PacketID.CLOSE.value, 
                DataType.NODA.value, 
                None
            ),
            is_async
        )
