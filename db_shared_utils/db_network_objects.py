from soldat_extmod_api.mod_api import Vector2D

class Serializable:
    def to_dict(self) -> dict:
        return self.__dict__
    
    @classmethod
    def from_dict(cls, dict: dict):
        return cls(**dict)

class RouteInfo(Serializable):
    def __init__(self, route_name, route_id, maintenance, checkpoint_list, map_name):
        self.route_name = route_name
        self.route_id = route_id
        self.maintenance = maintenance
        self.checkpoint_list = checkpoint_list
        self.map_name = map_name

    @property
    def spawn_point(self) -> Vector2D:
        return Vector2D(self.checkpoint_list[0][1], self.checkpoint_list[0][2])


class AccountInfo(Serializable):
    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash

class AdminInfo(Serializable):
    def __init__(self, password_hash: str, admin_password_hash: str):
        self.password_hash = password_hash
        self.admin_password_hash = admin_password_hash

class RecordInfo(Serializable):
    def __init__(self, record_time, route_id, map_name, password_hash):
        self.record_time = record_time
        self.route_id = route_id
        self.map_name = map_name
        self.password_hash = password_hash
