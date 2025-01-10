class Serializable:
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, dict: dict):
        return cls(**dict)

class RouteInfo(Serializable):
    def __init__(self, route_name, route_id, maintenance, checkpoint_list):
        self.route_name = route_name
        self.route_id = route_id
        self.maintenance = maintenance
        self.checkpoint_list = checkpoint_list

class AccountInfo(Serializable):
    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash

class AdminInfo(Serializable):
    def __init__(self, password_hash: str, admin_password_hash: str):
        self.password_hash = password_hash
        self.admin_password_hash = admin_password_hash

class RecordInfo(Serializable):
    def __init__(self, record_time, route_id, map_name, password_hash, snapshots_length):
        self.record_time = record_time
        self.route_id = route_id
        self.map_name = map_name
        self.password_hash = password_hash
        self.snapshots_length = snapshots_length