from db_shared_utils.db_shared import MOVEMENT_PLAYBACK_FREQUENCY
from replaybot_player import ReplayBot, ReplayData
from soldat_extmod_api.mod_api import ModAPI
from top_panel_ui.ui_top_constants import *
from db_cli import DBClient, PacketID
import time
from typing import TYPE_CHECKING
from threading import Lock

if TYPE_CHECKING:
    from general_ui.seek_bar_container import SeekBarContainer
    from top_panel_ui.score_row import ScoreRow

class ReplayManager:
    def __init__(self, mod_api: ModAPI, db_client: DBClient):
        self.bot_lock = Lock()
        self.mod_api = mod_api
        self.db_client = db_client
        self.bots : dict[tuple[str, int], ReplayBot] = {}
        self.username_replay_id_mapping: dict[int, str] = {}
        self.row_mapping: dict[tuple[str, int], ScoreRow] = {}
        self.last_tick_time = 0
        self.longest_replay_bot = None
        self.drag_pause = False
        self.db_client.client.register_subhandler(
            PacketID.NOTIFY_NEW_RECORD, 
            self.new_record_handler
        )
        self.db_client.client.register_subhandler(
            PacketID.REPLAY_UPLOAD, 
            self.replay_download_handler
        )
        self.top_data = None
        self.seek_bar: SeekBarContainer = None

    def __add_replay_internal(self, medal: Medal, replay_id: int, replay_data: ReplayData):
        if medal == Medal.NONE:
            skin_color = Color(0,0,0,0).to_int()
        else:
            color_rgba = medal_color_mapping.get(medal)
            color_argb = Color(
                color_rgba.alpha,
                color_rgba.red,
                color_rgba.green,
                color_rgba.blue
            )
            skin_color = color_argb.to_int()
        bot = ReplayBot()
        bot.add("ReplayBot", skin_color=skin_color)
        bot.replay_data = replay_data
        self.bots[(self.username_replay_id_mapping[replay_id], replay_id)] = bot
        bot.set_transparency(b"\xff")
        bot.play()

    def tick(self):
        if time.perf_counter() - self.last_tick_time >= MOVEMENT_PLAYBACK_FREQUENCY:
            self.last_tick_time = time.perf_counter()
            with self.bot_lock:
                if self.seek_bar:
                    if not self.seek_bar.replay_seek_bar.dragging:
                        if self.drag_pause and not self.seek_bar.seek_bar_button.paused:
                            self.drag_pause = False
                            self.play_all_bots()
                        bots = self.bots.values()
                        for bot in bots:
                            bot.inject_replay_movement()
                            if not bot.paused:
                                if bot.snapshot_index + 1 > bot.replay_max_index:
                                    if len(bots) > 1:
                                        bot.pause()
                                    else:
                                        bot.snapshot_index = 0
                                else:
                                    bot.snapshot_index += 1
                        all_finished = True
                        for bot in bots:
                            if bot.snapshot_index != bot.replay_max_index:
                                all_finished = False
                        if all_finished:
                            for bot in bots:
                                bot.snapshot_index = 0
                                bot.play()
                        if self.longest_replay_bot:
                            self.seek_bar.replay_seek_bar.knob.index = self.longest_replay_bot.snapshot_index
                            self.seek_bar.replay_seek_bar.knob.update_percentage(self.longest_replay_bot.snapshot_index * 2)
                            timestamp_current = self.__calc_timestamp_by_index(self.longest_replay_bot.snapshot_index)
                            self.seek_bar.time_stamp_current.update_text(timestamp_current)
                    else:
                        if not self.drag_pause:
                            self.pause_all_bots()
                        idx = self.seek_bar.replay_seek_bar.knob.index // 2
                        self.update_all_bots(idx)
                        self.seek_bar.replay_seek_bar.knob.update_percentage(self.longest_replay_bot.snapshot_index * 2)
                        self.seek_bar.time_stamp_current.update_text(self.__calc_timestamp_by_index(idx))

    def reset_all_replays(self):
        bots = self.bots.values()
        for bot in bots:
            bot.snapshot_index = 0
            bot.play()
        self.play_all_bots()

    def update_replay_data(self, replay_id: int, replay_data: ReplayData):
        bot = self.get_bot(replay_id)
        if bot:
            bot.replay_data = replay_data

    def new_record_handler(self, replay_id: int, _: float, route_id: int):
        bot = self.get_bot(replay_id)
        if bot:
            self.db_client.request_replay_download(replay_id, True)

    def replay_download_handler(self, replay_id, snap_count, replay_data):
        if snap_count:
            with self.bot_lock:
                bot = self.get_bot(replay_id)
                if bot:
                    # TODO: handle medal mismatch here
                    self.update_replay_data(replay_id, replay_data)
                else:
                    medal = self.top_data.player_medals[replay_id]
                    self.__add_replay_internal(medal, replay_id, replay_data)

                    if not self.top_data.top_panel_hidden:
                        keys = self.row_mapping.keys()
                        if keys:
                            key = [x for x in list(self.row_mapping.keys()) if x[1] == replay_id]
                            if key:
                                self.row_mapping[key[0]].replay_close_button.show()
                self.__seek_bar_replay_update_longest()

    def pause_bot(self, replay_id: int, username: str):
        bot = self.get_bot(replay_id, username)
        if bot:
            bot.pause()
            self.top_data.replay_states[(username, replay_id)] = False

    def play_bot(self, replay_id: int, username: str):
        bot = self.get_bot(replay_id, username)
        if bot:
            bot.play()
            self.top_data.replay_states[(username, replay_id)] = True

    def close_bot(self, replay_id: int, username: str):
        if (username, replay_id) in self.bots:
            bot = self.get_bot(replay_id, username)
            self.bots.pop((username, replay_id))
            del bot
        self.top_data.replay_states[(username, replay_id)] = False
        self.top_data.replay_existence_states[(username, replay_id)] = False
        self.row_mapping.pop((username, replay_id))
        if not self.bots:
            self.seek_bar.hide()
            self.longest_replay_bot = None
        else:
            self.__seek_bar_replay_update_longest()

    def add_replay(self, replay_id: int, username: str, row):
        self.username_replay_id_mapping[replay_id] = username
        self.db_client.request_replay_download(replay_id, True)
        self.row_mapping[(username, replay_id)] = row
        self.top_data.replay_states[(username, replay_id)] = True
        self.top_data.replay_existence_states[(username, replay_id)] = True

    def get_bot(self, replay_id: int, username: str = None):
        if not username and (username, replay_id) in self.bots:
            return self.bots[(username, replay_id)]
        keys = self.bots.keys()
        if keys:
            key = [x for x in list(self.bots.keys()) if x[1] == replay_id]
            if key:
                return self.bots[key[0]]

    def play_all_bots(self):
        for key in self.row_mapping:
            row = self.row_mapping[key]
            username = row.username
            replay_id = row.replay_id
            if username == key[0] and replay_id == key[1] and not row.hidden:
                row.replay_button.play()
            self.top_data.replay_states[(username, replay_id)] = True
        for bot in self.bots.values():
            bot.play()
        self.seek_bar.seek_bar_button.play()

    def pause_all_bots(self):
        for key in self.row_mapping:
            row = self.row_mapping[key]
            username = row.username
            replay_id = row.replay_id
            if username == key[0] and replay_id == key[1] and not row.hidden:
                row.replay_button.pause()
            self.top_data.replay_states[(username, replay_id)] = False
        for bot in self.bots.values():
            bot.pause()
        self.seek_bar.seek_bar_button.pause()

    def get_longest_replay(self) -> tuple[int, ReplayBot | None]:
        longest = max([replay.replay_max_index for replay in self.bots.values()])
        bot = [bot for bot in self.bots.values() if bot.replay_max_index == longest]
        bot = bot[0] if bot else None
        return longest, bot

    def update_all_bots(self, index: int):
        for bot in self.bots.values():
            if index > bot.replay_max_index:
                bot.snapshot_index = bot.replay_max_index
            else:
                bot.snapshot_index = index
            bot.inject_replay_movement()

    def __seek_bar_replay_update_longest(self):
        longest, bot = self.get_longest_replay()
        self.seek_bar.replay_seek_bar.knob.map_percentage(longest * 2)
        self.longest_replay_bot = bot
        self.seek_bar.time_stamp_end.update_text(self.__calc_timestamp_by_index(longest))
        self.seek_bar.seek_bar_button.play()
        self.seek_bar.show()

    def __calc_timestamp_by_index(self, index: int) -> str:
        time = round(index * MOVEMENT_PLAYBACK_FREQUENCY, ndigits=4)
        seconds = int(time)
        milliseconds = int((time % 1) * 1000)
        minutes = seconds // 60
        seconds %= 60
        hours = minutes // 60
        minutes %= 60
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}:{milliseconds:03d}"
        return timestamp
