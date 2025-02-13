from soldat_extmod_api.mod_api import ModAPI

from db_client.db_client import DBClient
from top_panel_ui.ui_top_constants import *

from replaybot_player import ReplayBot
from win_precise_time import time


class ReplayManager:
    def __init__(self, mod_api: ModAPI, db_client: DBClient):
        self.mod_api = mod_api
        self.db_client = db_client
        self.bots : dict[int, ReplayBot] = {}
        self.last_tick_time = 0

    def add_replay(self, medal: Medal, replay_id: int):
        replay_data = self.db_client.download_replay(replay_id)
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
        self.bots[replay_id] = bot
        bot.set_transparency(b"\xff")
        bot.play()

    def tick(self):
        if time() - self.last_tick_time >= 0.050:
            self.last_tick_time = time()
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

    def reset_all_replays(self):
        bots = self.bots.values()
        for bot in bots:
            bot.snapshot_index = 0
            bot.play()
