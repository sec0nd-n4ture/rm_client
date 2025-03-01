from soldat_extmod_api.mod_api import ModAPI, Event
from db_cli import DBClient, PacketID
from auth_ui.ui_account import AuthContainer
from mod_config import DB_SERVER_ADDRESS
from top_panel_ui.ui_top import TopPanel
from replay_manager import ReplayManager
from circular_menu import CircularMenu
from run_manager import RunManager
from map_manager import MapManager
import time
import sys

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
            print("Connected to DBServer")
        except:
            print("Couldn't connect to DBServer")
            sys.exit(1)
        self.db_client.start()

        self.replay_manager = ReplayManager(self.mod_api, self.db_client)

        ''' 
        This part patches the game to disable following functionalities:
        1 - punches by other players to avoid unwanted animation cancels.
        2 - sprite transparency updating for replay bots and applies to-
            every player that has id bigger or equal to/than 20 which-
            are the ids reserved for replay bots.
        '''

        self.mod_api.assembler.add_to_symbol_table(
            "bots_start_address", 
            self.mod_api.addresses["player_base"] + (SERVER_MAX_SLOTS * self.mod_api.addresses["player_size"])
        )
        self.mod_api.assembler.add_to_symbol_table(
            "AlphaHookContinue", self.mod_api.addresses["TransparencyUpdater"] + 18
        )
        self.mod_api.assembler.add_to_symbol_table(
            "ColHookContinue", self.mod_api.addresses["CollisionCheck"] + 0x8
        )

        patch_address = self.mod_api.patcher.patch(
            "custom_patches/transparency_patch.asm", "TransparencyUpdater", padding=13
        )

        '''
        This part is necessary to avoid executing in the middle of our jmp instruction
        caused by an earlier branch. The said branch does an unconditional jump to-
        our trampoline jump but a jump instruction is 5 bytes long, hence-
        invalidating the machine code leading to UB or crashes.
        '''

        self.mod_api.soldat_bridge.write(self.mod_api.addresses["TransparencyUpdater"]-1, b"\x05")
        self.mod_api.soldat_bridge.write(
            self.mod_api.addresses["TransparencyUpdater"]+5, 
            self.mod_api.assembler.assemble(
                f"jmp {hex(patch_address+12)}", 
                self.mod_api.addresses["TransparencyUpdater"]+5
            )
        )

        self.mod_api.patcher.patch(
            "custom_patches/collision_patch.asm", "CollisionCheck", padding=3
        )
        self.map_manager = MapManager(self.mod_api)
        self.mod_api.event_dispatcher.map_manager = self.map_manager
        self.db_client.client.register_subhandler(PacketID.RECORD_FETCH, self.map_manager.set_own_time)
        self.db_client.client.register_subhandler(PacketID.ROUTE_FETCH, self.route_list_response)
        self.db_client.client.register_subhandler(PacketID.NOTIFY_NEW_RECORD, self.new_record_handler)

        self.main_loop()

    
    def main_loop(self):
        while True:
            try:
                if hasattr(self, "circular_menu"):
                    self.circular_menu.update_transitions()
                if hasattr(self, "run_manager"):
                    self.run_manager.tick()
                if hasattr(self, "replay_manager"):
                    self.replay_manager.tick()
                self.mod_api.tick_event_dispatcher()
                time.sleep(0.0001)
            except KeyboardInterrupt:
                break
        sys.exit(1)

# Callbacks -----------------------------------
    def on_directx_ready(self):
        self.auth_container = AuthContainer(self.mod_api, self.db_client)
        self.circular_menu = CircularMenu(self.mod_api, self.mod_api.get_gui_frame())
        self.auth_container.login_success_callback = self.on_login_success
        self.top_panel = TopPanel(self.mod_api, self.map_manager, self.replay_manager, self.db_client, 275, -50)
        self.top_panel.top_page_change_callback = self.on_page_change
        # self.db_client.client.register_subhandler(PacketID.TOP_PLACEMENT, self.top_panel.display_top_data)
        self.circular_menu.top_panel_button.set_action_callback(self.top_panel.hide)
        self.circular_menu.top_panel_button.toggled_action_callback(self.top_panel.show)
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
        for bot in self.replay_manager.bots.values():
            bot.deactivate()
            bot.free()
        self.replay_manager.bots.clear()
        self.replay_manager.row_mapping.clear()
        self.replay_manager.username_replay_id_mapping.clear()

        self.top_panel.top_manager.replay_existence_states.clear()
        self.top_panel.top_manager.player_medals.clear()
        self.top_panel.top_manager.replay_states.clear()

        self.db_client.request_routes(map_name, True)
        self.map_manager.selected_route = 0
        if hasattr(self, "auth_container") and hasattr(self.auth_container, "cookie"):
            self.db_client.request_own_record(
                self.map_manager.current_map_name, 
                self.map_manager.get_current_route().route_id,
                self.auth_container.cookie,
                True
            )

        self.top_panel.page = 0

        self.db_client.request_top(-1, map_name, self.top_panel.page, True)

    def on_login_success(self):
        self.map_manager.cookie = self.auth_container.cookie
        self.run_manager = RunManager(
            self.mod_api, self.map_manager, 
            self.replay_manager, self.db_client
        )
        self.db_client.request_own_record(
            self.map_manager.current_map_name, 
            -1,
            self.auth_container.cookie,
            True
        )

    def on_page_change(self):
        self.db_client.request_top(-1, self.map_manager.current_map_name, self.top_panel.page, True)

    def route_list_response(self, routes):
        self.map_manager.routes = routes
        cps = self.map_manager.populate_checkpoints()
        self.mod_api.event_dispatcher.checkpoints = cps

    def new_record_handler(self, replay_id: int, _, route_id: int):
        self.db_client.request_top(
            route_id, 
            self.map_manager.current_map_name, 
            self.top_panel.page, 
            True
        )
# ----------------------------------------------------------------------

if __name__ == "__main__":
    main = ModMain()
