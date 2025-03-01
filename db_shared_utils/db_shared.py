from enum import Enum, auto
import hashlib

MOVEMENT_RECORDING_FREQUENCY = 0.050
MOVEMENT_PLAYBACK_FREQUENCY = 0.050

class ReplayData:
    snapshot_size = 33
    def __init__(self):
        self.data: bytes = b""

    def __iadd__(self, data_snapshot: bytes):
        self.data += data_snapshot
        return self

    def __len__(self):
        return len(self.data)

    def set_data(self, data: bytes):
        self.data = data

    def get_mouse_pos(self, index: int) -> bytes:
        return self.data[index*ReplayData.snapshot_size:][:4]

    def get_position(self, index: int) -> bytes:
        return self.data[index*ReplayData.snapshot_size:][4:12]

    def get_velocity(self, index: int) -> bytes:
        return self.data[index*ReplayData.snapshot_size:][12:20]

    def get_first_keystates(self, index: int) -> bytes:
        return self.data[index*ReplayData.snapshot_size:][20:24]

    def get_second_keystates(self, index: int) -> bytes:
        return self.data[index*ReplayData.snapshot_size:][24:33]

    @property
    def get_snapshots_len(self):
        if len(self.data) == 0:
            return 0
        return (len(self.data) // ReplayData.snapshot_size)

    def load(self, file_name: str):
        with open(file_name, "rb") as fd:
            self.set_data(fd.read())

    def save(self, file_name: str):
        with open(file_name, "wb") as fd:
            fd.write(self.data)

    def scrap(self):
        self.data = b""

    @classmethod
    def copy(cls, replay_data: 'ReplayData'):
        replay_copy = cls()
        replay_copy.data = replay_data.data
        return replay_copy

    def truncate(self):
        lenght = len(self)
        excess = lenght % ReplayData.snapshot_size
        if lenght > ReplayData.snapshot_size and excess:
            self.data = self.data[0:len(self.data) - excess]

class PacketID(Enum):
    ACCOUNT_CREATION = auto()
    AUTHENTICATION = auto()
    RECORD_UPDATE = auto()
    RECORD_FETCH = auto()
    RECORD_FETCH_BEST = auto()
    REPLAY_UPLOAD = auto()
    REPLAY_DOWNLOAD = auto()
    TOP_PLACEMENT = auto()
    NOTIFY_NEW_RECORD = auto()
    RECORD_EVENT_SUBSCRIBTION = auto()
    ROUTE_FETCH = auto()
    ACCOUNT_ELEVATION = auto()
    GET_UPDATES = auto()
    ADD_ROUTE = auto()
    DEL_ROUTE = auto()
    EDIT_ROUTE = auto()
    SWITCH_ROUTE_MAINTENANCE = auto()
    CLOSE = auto()
    UNKNOWN = auto()

class DataType(Enum):
    JSON = auto()
    BLOB = auto()
    NODA = auto()

def hash_password(password: str, username: str):
    salt = username
    return hashlib.sha256((password + salt).encode()).digest()
