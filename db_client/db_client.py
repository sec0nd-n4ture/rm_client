import socket
from db_shared_utils.db_shared import *
from db_shared_utils.db_network_objects import *
from struct import unpack
import json
import hashlib
from enum import Enum, auto
from collections.abc import Callable

class UpdateType(Enum):
    NEW_RECORD = auto()
    ROUTE_CHANGE = auto()
    ROUTE_MAINTENANCE = auto()


MAX_RECONNECT_RETRY = 7
TIMEOUT = 10
RECV_BUFFER_SIZE = 4096
UPDATE_CHECK_DELAY = 0.5

class DBClient:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)
        self.connected = False
        self.callbacks: dict[UpdateType, list[Callable]] = {}

    def get_callbacks_by_type(self, type: UpdateType) -> list[Callable] | None:
        return self.callbacks.get(type) if self.callbacks and type in self.callbacks and self.callbacks[type] else None

    def add_callbacks_by_type(self, type: UpdateType, callback: Callable):
        if type not in self.callbacks:
            self.callbacks[type] = []
        self.callbacks[type].append(callback)

    def connect(self):
        retry_count = 0
        while not self.connected and retry_count < MAX_RECONNECT_RETRY:
            try:
                self.socket.connect((self.ip, self.port))
                self.connected = True
                print("Connected to DBServer")
                break
            except:
                retry_count += 1
                print(f"DBClient reconnecting, retries: {retry_count}")
        if not self.connected:
            raise DBClient.MaxRetriesReachedError("Max retries reached while connecting to the DBServer.")
    
    def __receive(self, size: int = RECV_BUFFER_SIZE):
        if not self.connected:
            raise DBClient.NotConnectedError("Call to receive when not connected.") 
        data = self.socket.recv(size)
        if data: return data

    def __send(self, data: bytes):
        if not self.connected:
            raise DBClient.NotConnectedError("Call to send when not connected.")
        self.socket.send(data)

    def register(self, username, password) -> bytes:
        password_hash = hash_password(password, username)
        info = AccountInfo(username, password_hash.hex())
        data = json.dumps(info.to_dict()).encode()
        self.__send(PacketID.ACCOUNT_CREATION.value + data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return password_hash
        elif resp == ResponseID.ACCOUNT_EXISTS.value:
            raise DBClient.AccountExistsError("Account already exists.")

    def login(self, username, password) -> bytes:
        password_hash = hash_password(password, username)
        info = AccountInfo(username, password_hash.hex())
        data = json.dumps(info.to_dict()).encode()
        self.__send(PacketID.AUTHENTICATION.value + data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return password_hash
        elif resp == ResponseID.WRONG_CREDS.value:
            raise DBClient.WrongCredentialsError("Wrong credentials.")

    def update_record(self, record_time: float, 
                      route_id: int, pw_hash: bytes, 
                      map_name: str, replay_data: ReplayData):
        record_info = RecordInfo(record_time, route_id, map_name, pw_hash.hex(), replay_data.get_snapshots_len)
        data = json.dumps(record_info.to_dict()).encode()
        self.__send(PacketID.RECORD_UPDATE.value + data)
        resp = self.__receive(1)
        if resp == ResponseID.PROCEED.value:
            offset = 0
            while offset < len(replay_data):
                end = offset + REPLAY_DATA_CHUNK_SIZE
                chunk = replay_data.data[offset:end]
                self.__send(chunk)
                offset += len(chunk)
            resp = self.__receive(1)
            if resp == ResponseID.SUCCESS.value:
                return True
            elif resp == ResponseID.VERIFICATION_FAILURE.value:
                return False
            elif resp == ResponseID.NOT_AUTHENTICATED.value:
                return False
            return False
        elif resp == ResponseID.INVALID_PARAMETERS.value:
            raise DBClient.InvalidParametersError("Invalid parameters were passed.")
        else:
            raise DBClient.RecordUpdateFailedError()

    def get_routes(self, map_name: str) -> list[RouteInfo]:
        data = PacketID.ROUTE_FETCH.value + json.dumps({"map_name": map_name}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            route_data = self.__receive()
            route_data = json.loads(route_data)
            return [RouteInfo.from_dict(route_dict) for route_dict in route_data]
        elif resp == ResponseID.ROUTE_NOT_FOUND.value:
            return None

    def get_top(self, route_id: int, map_name: str, page: int = 0) -> dict:
        data = PacketID.TOP_PLACEMENT.value + json.dumps({"route_id": route_id, "page": page, "map_name": map_name}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            top_data = self.__receive()
            top_data = json.loads(top_data)
            return top_data
        elif resp == ResponseID.RECORD_NOT_FOUND.value:
            return None
        
    def get_own_record(self, map_name: str, route_id: int, pw_hash: bytes) -> float | None:
        data = PacketID.RECORD_FETCH.value
        data += json.dumps({
            "map_name": map_name,
            "route_id": route_id,
            "password_hash": pw_hash.hex()
        }).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            record_data = self.__receive()
            record_data = json.loads(record_data)
            return record_data["record_time"]
        elif resp == ResponseID.RECORD_NOT_FOUND.value:
            return None
        
    def download_replay(self, replay_id: int) -> ReplayData:
        data = PacketID.REPLAY_DOWNLOAD.value + json.dumps({"replay_id": replay_id}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            replay_data = ReplayData()
            size = self.__receive(4)
            size = unpack("I", size)[0] * replay_data.snapshot_size
            while len(replay_data) < size:
                chunk = self.__receive(REPLAY_DATA_CHUNK_SIZE)
                replay_data.data += chunk
            return replay_data
        elif resp == ResponseID.REPLAY_NOT_FOUND.value:
            raise DBClient.ReplayNotFoundError(f"Replay with id {replay_id} not found.")
            
    def get_updates(self) -> dict[str, list] | None:
        data = PacketID.GET_UPDATES.value
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            update_data = self.__receive()
            update_data = json.loads(update_data)
            return update_data

    def elevate_account(self, admin_password: str, cookie: bytes):
        data = PacketID.ACCOUNT_ELEVATION.value
        admin_info = AdminInfo(cookie.hex(), hashlib.sha256(admin_password.encode()).hexdigest())
        data += json.dumps(admin_info.to_dict()).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            self.elevated = True
            return True
        elif resp == ResponseID.WRONG_CREDS.value:
            raise DBClient.WrongCredentialsError("Wrong administrator password.")
        return False

    def enable_route_maintenance(self, route_id: int, pw_hash: bytes):
        data = PacketID.SWITCH_ROUTE_MAINTENANCE.value
        data += json.dumps({"route_id": route_id, "state": 1, "password_hash": pw_hash.hex()}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return True
        elif resp == ResponseID.ROUTE_NOT_FOUND.value:
            return False
        elif resp == ResponseID.NOT_PERMITTED.value: # not admin
            return False

    def disable_route_maintenance(self, route_id: int, pw_hash: bytes):
        data = PacketID.SWITCH_ROUTE_MAINTENANCE.value
        data += json.dumps({"route_id": route_id, "state": 0, "password_hash": pw_hash.hex()}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return True
        elif resp == ResponseID.ROUTE_NOT_FOUND.value:
            return False
        elif resp == ResponseID.NOT_PERMITTED.value: # not admin
            return False

    def edit_route(self, route_id: int, checkpoints: list[list[int, float, float]], pw_hash: bytes, route_name: str = None):
        data = PacketID.EDIT_ROUTE.value
        data += json.dumps({"route_id": str(route_id),
                            "password_hash": pw_hash.hex(), 
                            "checkpoint_list": checkpoints, 
                            "route_name": str(route_name)}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return True
        elif resp == ResponseID.ROUTE_NOT_FOUND.value:
            return False
        elif resp == ResponseID.NOT_PERMITTED.value:
            return False

    def add_route(self, map_name: str, checkpoints: list[list[int, float, float]], pw_hash: bytes, route_name: str = None):
        data = PacketID.ADD_ROUTE.value
        route_info_dict = {}
        route_info_dict["checkpoint_list"] = checkpoints
        route_info_dict["route_name"] = str(route_name)
        route_info_dict["map_name"] = map_name
        route_info_dict["password_hash"] = pw_hash.hex()
        data += json.dumps(route_info_dict).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return True
        elif resp == ResponseID.NOT_PERMITTED.value:
            return False
        elif resp == ResponseID.EXISTING_ROUTE.value:
            return False

    def delete_route(self, route_id: int, pw_hash: bytes):
        data = PacketID.DEL_ROUTE.value
        data += json.dumps({"route_id": route_id, "password_hash": pw_hash.hex()}).encode()
        self.__send(data)
        resp = self.__receive(1)
        if resp == ResponseID.SUCCESS.value:
            return True
        elif resp == ResponseID.ROUTE_NOT_FOUND.value:
            return False
        elif resp == ResponseID.NOT_PERMITTED.value: # not admin
            return False
        
    def update_check(self):
        updates = self.get_updates()
        if "replay_ids" in updates and updates["replay_ids"]:
            for callback in self.get_callbacks_by_type(UpdateType.NEW_RECORD):
                callback(updates["replay_ids"])
        if "route_change" in updates and updates["route_change"]:
            for callback in self.get_callbacks_by_type(UpdateType.ROUTE_CHANGE):
                callback(updates["route_change"])
        if "maintenance" in updates and updates["maintenance"]:
            for callback in self.get_callbacks_by_type(UpdateType.ROUTE_MAINTENANCE):
                callback(updates["maintenance"])

    def subscribe_updates(self, callback: Callable, update_type: UpdateType):
        self.add_callbacks_by_type(update_type, callback)

    def close(self):
        data = PacketID.CLOSE.value
        self.__send(data)
        self.connected = False

    class MaxRetriesReachedError(BaseException):
        pass
        
    class TimeoutError(BaseException):
        pass

    class RefusedError(Exception):
        pass

    class ConnectionResetError(BaseException):
        pass

    class InvalidParametersError(BaseException):
        pass

    class NotConnectedError(BaseException):
        pass

    class AccountExistsError(Exception):
        pass

    class RecordUpdateFailedError(Exception):
        pass

    class ReplayNotFoundError(Exception):
        pass

    class WrongCredentialsError(Exception):
        pass
