from db_client.db_client import DBClient, UPDATE_CHECK_DELAY
from soldat_extmod_api.mod_api import ModAPI, Event
from auth_ui.ui_account import AuthContainer
from circular_menu import CircularMenu
from map_manager import MapManager
import win_precise_time
import sys

DB_SERVER_ADDRESS = ("127.0.0.1", 23999)
SERVER_MAX_SLOTS = 20


class ModMain:
    def __init__(self) -> None:
        self.mod_api = ModAPI()
        self.mod_api.subscribe_event(self.on_directx_ready, Event.DIRECTX_READY)
        self.mod_api.subscribe_event(self.on_lcontrol_down, Event.LCONTROL_DOWN)
        self.mod_api.subscribe_event(self.on_lcontrol_up, Event.LCONTROL_UP)
        self.mod_api.subscribe_event(self.on_map_change, Event.MAP_CHANGE)

        self.freeze_cam = False
        self.db_client = DBClient(*DB_SERVER_ADDRESS)
        try:
            self.db_client.connect()
        except DBClient.MaxRetriesReachedError:
            sys.exit(1)

        self.mod_api.assembler.add_to_symbol_table(
            "bots_start_address", 
            self.mod_api.addresses["player_base"] + (SERVER_MAX_SLOTS * self.mod_api.addresses["player_size"])
        )
        self.mod_api.assembler.add_to_symbol_table(
            "AlphaHookContinue", self.mod_api.addresses["TransparencyUpdater"] + 0x6
        )
        self.mod_api.assembler.add_to_symbol_table(
            "ColHookContinue", self.mod_api.addresses["CollisionCheck"] + 0x6
        )

        self.mod_api.patcher.patch(
            "custom_patches/transparency_patch.asm", "TransparencyUpdater", padding=3
        )
        self.mod_api.patcher.patch(
            "custom_patches/collision_patch.asm", "CollisionCheck", padding=3
        )
        self.map_manager = MapManager(self.mod_api, self.db_client)
        self.mod_api.event_dispatcher.map_manager = self.map_manager

        self.main_loop()

    
    def main_loop(self):
        t1 = win_precise_time.time()
        while True:
            try:
                if hasattr(self, "circular_menu"):
                    self.circular_menu.update_transitions()
                self.mod_api.tick_event_dispatcher()
                t2 = win_precise_time.time()
                if (t2 - t1) >= UPDATE_CHECK_DELAY:
                    self.db_client.update_check()
                    t1 = t2
            except KeyboardInterrupt:
                break
        sys.exit(1)

    def on_directx_ready(self):
        self.auth_container = AuthContainer(self.mod_api, self.db_client)
        self.circular_menu = CircularMenu(self.mod_api, self.mod_api.get_gui_frame())
        self.mod_api.enable_drawing()

    def on_lcontrol_down(self):
        if not self.freeze_cam:
            self.mod_api.take_cursor_controls()
            self.mod_api.take_camera_controls()
            self.freeze_cam = True

    def on_lcontrol_up(self):
        self.mod_api.restore_cursor_controls()
        self.mod_api.restore_camera_controls()
        self.freeze_cam = False

    def on_map_change(self, map_name: str):
        self.map_manager.routes = self.db_client.get_routes(map_name)
        self.map_manager.selected_route = 0
        cps = self.map_manager.populate_checkpoints()
        self.mod_api.event_dispatcher.checkpoints = cps

if __name__ == "__main__":
    main = ModMain()
