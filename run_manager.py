from soldat_extmod_api.mod_api import ModAPI, Event, Vector2D
from db_shared_utils.db_shared import ReplayData
from db_cli import DBClient
from replay_manager import ReplayManager
from map_manager import MapManager
from rm_player import RmPlayer
import time


class RunManager:
    def __init__(
            self, 
            mod_api: ModAPI, 
            map_manager: MapManager, 
            replay_manager: ReplayManager,
            db_client: DBClient
        ):
        self.mod_api = mod_api
        self.map_manager = map_manager
        self.replay_manager = replay_manager
        self.db_client = db_client
        self.mod_api.subscribe_event(self.on_run_start, Event.RUN_START)
        self.mod_api.subscribe_event(self.on_run_finish, Event.RUN_FINISH)
        self.mod_api.subscribe_event(self.on_r_key_up, Event.R_KEY_UP)
        self.mod_api.subscribe_event(self.on_respawn, Event.PLAYER_RESPAWN)
        self.own_player = RmPlayer(self.mod_api, self.mod_api.get_own_id())
        self.timer = Timer()
        self.replay_buffer = ReplayData()
        self.__past_time = 0
        self.pause_recording = False

# Callbacks -----------------------------------
    def on_run_start(self):
        self.replay_buffer.scrap()
        self.timer.reset()

    def on_run_finish(self):
        run_time = self.timer.get_time_elapsed()
        self.pause_recording = True
        route_own_time = self.map_manager.route_own_time
        if not route_own_time or run_time <= route_own_time:
            self.db_client.update_record(
                run_time,
                self.map_manager.get_current_route().route_id,
                self.map_manager.cookie,
                self.map_manager.current_map_name,
                ReplayData.copy(self.replay_buffer),
                True
            )
            self.db_client.request_own_record(
                self.map_manager.current_map_name, 
                self.map_manager.get_current_route().route_id,
                self.map_manager.cookie,
                True
            )
        print(round(run_time, ndigits=3))
        self.restart_run()

    def on_r_key_up(self):
        self.restart_run()

    def on_respawn(self):
        self.restart_run()
# ----------------------------------------------------------------------

    def restart_run(self):
        self.replay_buffer.scrap()
        if self.mod_api.event_dispatcher.checkpoints:
            for checkpoint in self.mod_api.event_dispatcher.checkpoints:
                checkpoint.deactivate()
        self.own_player.respawn()
        self.own_player.set_position(self.map_manager.get_current_route().spawn_point)
        self.own_player.set_velocity(Vector2D.zero())
        self.pause_recording = False
        self.replay_manager.reset_all_replays()

    def tick(self):
        elapsed = time.perf_counter() - self.__past_time
        if elapsed >= 0.050:
            self.__past_time = time.perf_counter()
            if not self.pause_recording:
                self.replay_buffer += self.own_player.take_movement_snapshot() # should be a lock here


class Timer:
    def __init__(self):
        self.time = time.perf_counter()

    def get_time_elapsed(self):
        return time.perf_counter() - self.time
    
    def reset(self):
        self.time = time.perf_counter()
