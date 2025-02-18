from typing import TYPE_CHECKING
from auth_ui.auth_ui_constants import CREDS_SAVEFILE
from soldat_extmod_api.mod_api import ModAPI, Vector2D

from db_client.db_client import DBClient, ReplayData
from replay_manager import ReplayManager, Medal
from map_manager import MapManager
from info_provider.job import Job
import json

if TYPE_CHECKING:
    from auth_ui.ui_account import AuthContainer
    from top_panel_ui.ui_top import TopPanel


class TopDataDisplayJob(Job):
    def __init__(
            self, 
            db_client: DBClient, 
            top_panel: 'TopPanel',
            map_manager: MapManager
        ):
        self.db_client = db_client
        self.top_panel = top_panel
        self.map_manager = map_manager

    def execute(self):
        self.top_panel.display_top_data(
            self.db_client.get_top(
                -1, 
                self.map_manager.current_map_name, 
                self.top_panel.page
            )
        )

class UpdateReplayDataJob(Job):
    def __init__(
            self, 
            db_client: DBClient, 
            replay_manager: ReplayManager,
            replay_ids: list[int]
        ):
        self.db_client = db_client
        self.replay_manager = replay_manager
        self.replay_ids = replay_ids

    def execute(self):
        for replay_id in self.replay_ids:
            if replay_id in self.replay_manager.bots:
                self.replay_manager.bots[replay_id].replay_data = self.db_client.download_replay(replay_id)

class CheckpointPopulationJob(Job):
    def __init__(
            self,
            db_client: DBClient,
            map_manager: MapManager,
            mod_api: ModAPI,
            map_name: str
        ):
        self.db_client = db_client
        self.map_manager = map_manager
        self.mod_api = mod_api
        self.map_name = map_name

    def execute(self):
        self.map_manager.routes = self.db_client.get_routes(self.map_name)
        self.map_manager.selected_route = 0
        cps = self.map_manager.populate_checkpoints()
        self.mod_api.event_dispatcher.checkpoints = cps

class AddReplaybotJob(Job):
    def __init__(
            self,
            replay_manager: ReplayManager,
            medal: Medal,
            replay_id: int
        ):
        self.replay_manager = replay_manager
        self.medal = medal
        self.replay_id = replay_id

    def execute(self):
        self.replay_manager.add_replay(self.medal, self.replay_id)

class RecordUpdateJob(Job):
    def __init__(
            self,
            db_client: DBClient,
            map_manager: MapManager,
            replay_buffer: ReplayData,
            run_time: float
        ):
        self.db_client = db_client
        self.map_manager = map_manager
        self.replay_buffer = replay_buffer
        self.run_time = run_time

    def execute(self):
        route_own_time = self.map_manager.route_own_time
        self.db_client.update_record(
            self.run_time, 
            self.map_manager.get_current_route().route_id, 
            self.map_manager.cookie, 
            self.map_manager.current_map_name, 
            self.replay_buffer
        ) if not route_own_time or self.run_time <= route_own_time else None

class AuthInfoSubmitJob(Job):
    def __init__(self, auth_container: 'AuthContainer'):
        self.auth_container = auth_container

    def execute(self) -> None:
        is_login = self.auth_container.confirm_field.hidden
        if is_login:
            try:
                res = self.auth_container.login(
                    self.auth_container.username_field.input_text, 
                    self.auth_container.password_field.true_text
                )
                if res:
                    if self.auth_container.checkbox.checked:
                        with open(CREDS_SAVEFILE, "w") as f:
                            json.dump({"username": self.auth_container.username_field.input_text,
                                       "password": res.hex()} , f, indent=4)
                    self.auth_container.cookie = res
                    self.auth_container.login_success_callback()
                    self.auth_container.hide()
                    self.auth_container.submit_button.text.set_text("Elevate Account")
                    self.auth_container.submit_button.text.set_pos(
                        self.auth_container.submit_button.text.text_position.sub(Vector2D(53, 0))
                    )
                    self.auth_container.title_text.set_text("Account")
                else:
                    self.auth_container.display_status("All fields must be filled.", False)
            except DBClient.WrongCredentialsError as e:
                self.auth_container.display_status(str(e), False)

        if not is_login:
            if self.auth_container.password_field.true_text != self.auth_container.confirm_field.true_text:
                self.auth_container.display_status("Passwords do not match.", False)
            else:
                try:
                    res = self.auth_container.register(
                        self.auth_container.username_field.input_text, 
                        self.auth_container.password_field.true_text, 
                        self.auth_container.confirm_field.true_text
                    )
                    if res:
                        self.auth_container.display_status("Successfully registered.", True)
                        self.auth_container.switch_button.switch()
                    else:
                        self.auth_container.display_status("All fields must be filled.", False)
                except DBClient.AccountExistsError as e:
                    self.auth_container.display_status(str(e), False)
