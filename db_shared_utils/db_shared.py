from enum import Enum
import hashlib

REPLAY_DATA_CHUNK_SIZE = 4096
MOVEMENT_RECORDING_FREQUENCY = 0.050
MOVEMENT_PLAYBACK_FREQUENCY = 0.050

class ReplayData:
    def __init__(self):
        self.data: bytes = b""
        self.snapshot_size = 33

    def __iadd__(self, data_snapshot: bytes):
        self.data += data_snapshot
        return self
    
    def __len__(self):
        return len(self.data)

    def set_data(self, data: bytes):
        self.data = data

    def get_mouse_pos(self, index: int) -> bytes:
        return self.data[index*self.snapshot_size:][:4]
    
    def get_position(self, index: int) -> bytes:
        return self.data[index*self.snapshot_size:][4:12]
    
    def get_velocity(self, index: int) -> bytes:
        return self.data[index*self.snapshot_size:][12:20]
    
    def get_first_keystates(self, index: int) -> bytes:
        return self.data[index*self.snapshot_size:][20:24]
    
    def get_second_keystates(self, index: int) -> bytes:
        return self.data[index*self.snapshot_size:][24:33]
    
    @property
    def get_snapshots_len(self):
        if len(self.data) == 0:
            return 0
        return (len(self.data) // self.snapshot_size) - 1
    
    def load(self, file_name: str):
        with open(file_name, "rb") as fd:
            self.set_data(fd.read())

    def save(self, file_name: str):
        with open(file_name, "wb") as fd:
            fd.write(self.data)

    def scrap(self):
        self.data = b""

class PacketID(Enum):
    ACCOUNT_CREATION = b"\x00"
    AUTHENTICATION = b"\x01"
    RECORD_UPDATE = b"\x02"
    RECORD_FETCH = b"\x03"
    RECORD_FETCH_BEST = b"\x04"
    REPLAY_UPLOAD = b"\x05"
    REPLAY_DOWNLOAD = b"\x06"
    TOP_PLACEMENT = b"\x07"
    NOTIFY_NEW_RECORD = b"\x08"
    RECORD_EVENT_SUBSCRIBTION = b"\x09"
    ROUTE_FETCH = b"\x0A"
    ACCOUNT_ELEVATION = b"\x0B"
    GET_UPDATES = b"\x0C"
    ADD_ROUTE = b"\x0D"
    DEL_ROUTE = b"\x0E"
    EDIT_ROUTE = b"\x0F"
    SWITCH_ROUTE_MAINTENANCE = b"\x10"
    CLOSE = b"\x11"

class ResponseID(Enum):
    SUCCESS = b"\x00"
    ACCOUNT_EXISTS = b"\x01"
    NOT_AUTHENTICATED = b"\x02"
    UNKNOWN_PACKET_ID = b"\x03"
    WRONG_CREDS = b"\x04"
    INVALID_PARAMETERS = b"\x05"
    RECORD_NOT_FOUND = b"\x06"
    PROCEED = b"\x07"
    REPLAY_NOT_FOUND = b"\x08"
    ROUTE_NOT_FOUND = b"\x09"
    VERIFICATION_FAILURE = b"\x0A"
    NOT_PERMITTED = b"\x0B"
    EXISTING_ROUTE = b"\x0C"

def hash_password(password: str, username: str):
    salt = username
    return hashlib.sha256((password + salt).encode()).digest()
