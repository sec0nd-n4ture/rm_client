from soldat_extmod_api.graphics_helper.vector_utils import Vector2D
from db_shared_utils.db_network_objects import RouteInfo
from checkpoint import CheckPoint
from soldat_extmod_api.mod_api import ModAPI
from soldat_extmod_api.graphics_helper.color import RED

CHECKPOINT_SCALE = 0.6

class MapManager:
    def __init__(self, mod_api: ModAPI):
        self.mod_api = mod_api
        self.soldat_bridge = self.mod_api.soldat_bridge
        self.map_name_len_addr = self.mod_api.addresses["current_map_name_length"]
        self.map_name_addr = self.mod_api.addresses["current_map_name"]
        self.selected_route = 0
        self.routes: list[RouteInfo] = []
        self.cookie: bytes = None
        self.route_own_time: float = None

    @property
    def current_map_name(self) -> str:
        name_length = int.from_bytes(
            self.soldat_bridge.read(self.map_name_len_addr, 1), 
            "little"
        )
        if name_length > 0:
            map_name = self.soldat_bridge.read(
                self.map_name_addr, name_length
            )
            return map_name.decode("utf-8")
        else:
            while name_length == 0:
                name_length = int.from_bytes(
                    self.soldat_bridge.read(self.map_name_len_addr, 1), 
                    "little"
                )
            map_name = self.soldat_bridge.read(
                self.map_name_addr, name_length
            )
            return map_name.decode("utf-8")

    def set_own_time(self, result: bool, record_time: float):
        if result:
            self.route_own_time = record_time

    def populate_checkpoints(self) -> list[CheckPoint]:
        cps: list[CheckPoint] = []
        for checkpoint_info in self.routes[self.selected_route].checkpoint_list:
            cp = CheckPoint(Vector2D(checkpoint_info[1], checkpoint_info[2]), 
                            Vector2D(CHECKPOINT_SCALE, CHECKPOINT_SCALE), 
                            RED, checkpoint_info[0], self.mod_api)
            cps.append(cp)
        if cps: CheckPoint.connect_checkpoints(*cps)
        return cps
    
    def get_current_route(self) -> RouteInfo:
        return self.routes[self.selected_route] if self.routes else None
