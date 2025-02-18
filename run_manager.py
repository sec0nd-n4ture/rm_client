from soldat_extmod_api.mod_api import ModAPI, Event, Vector2D
from info_provider.info_provider import InfoProvider
from db_shared_utils.db_shared import ReplayData
from replay_manager import ReplayManager
from map_manager import MapManager
from jobs import RecordUpdateJob
from rm_player import RmPlayer
import win_precise_time


class RunManager:
    def __init__(
            self, 
            mod_api: ModAPI, 
            map_manager: MapManager, 
            replay_manager: ReplayManager,
            info_provider: InfoProvider
        ):
        self.mod_api = mod_api
        self.map_manager = map_manager
        self.replay_manager = replay_manager
        self.db_client = map_manager.db_client
        self.info_provider = info_provider
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
        self.info_provider.submit_job(
            RecordUpdateJob(
                self.db_client,
                self.map_manager,
                ReplayData.copy(self.replay_buffer),
                run_time
            )
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
        elapsed = win_precise_time.time() - self.__past_time
        if elapsed >= 0.050:
            self.__past_time = win_precise_time.time()
            if not self.pause_recording:
                self.replay_buffer += self.own_player.take_movement_snapshot()


class Timer:
    def __init__(self):
        self.time = win_precise_time.time()

    def get_time_elapsed(self):
        return win_precise_time.time() - self.time
    
    def reset(self):
        self.time = win_precise_time.time()
