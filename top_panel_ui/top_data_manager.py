from db_cli import DBClient, PacketID
from top_panel_ui.score_row import ScoreRow
from top_panel_ui.ui_top_constants import *


class TopData:
    def __init__(self, db_client: DBClient, score_rows: list[ScoreRow]) -> None:
        self.score_rows = score_rows
        self.db_client = db_client
        self.db_client.client.register_subhandler(PacketID.TOP_PLACEMENT, self.top_data_handler)
        self.replay_states: dict[tuple[str, int], bool] = {} # paused or playing state
        self.replay_existence_states: dict[tuple[str, int], bool] = {}
        self.player_medals: dict[int, Medal] = {}
        self.page = 0
        self.top_panel_hidden = False

    def top_data_handler(self, data):
        if not self.top_panel_hidden:
            keys = list(data.keys()) if data else []
            entries_length = len(keys) - 1
            for i in range(10):
                if data:
                    if i > entries_length:
                        self.score_rows[i].hide()
                    else:
                        self.score_rows[i].switch_top3_state(self.page == 0)
                        r_id = data[keys[i]]["replay_id"]
                        self.score_rows[i].set_username(keys[i])
                        self.score_rows[i].set_record_time(data[keys[i]]["record_time"])
                        self.score_rows[i].set_place_text(i+(self.page * 10)+1)
                        self.score_rows[i].replay_id = r_id
                        self.score_rows[i].show()
                        if self.page == 0:
                            self.player_medals[r_id] = self.score_rows[i].medal
                        else:
                            self.player_medals[r_id] = Medal.NONE
                        if (keys[i], r_id) not in self.replay_states:
                            self.replay_states[(keys[i], r_id)] = False
                            self.score_rows[i].replay_button.pause()
                        if (keys[i], r_id) not in self.replay_existence_states:
                            self.replay_existence_states[((keys[i], r_id))] = False
                        is_playing = self.replay_states[(keys[i], r_id)]
                        replay_exists = self.replay_existence_states[(keys[i], r_id)]
                        if is_playing:
                            self.score_rows[i].replay_button.play()
                        else:
                            self.score_rows[i].replay_button.pause()
                        if replay_exists:
                            self.score_rows[i].replay_close_button.show()
                        else:
                            self.score_rows[i].replay_close_button.hide()

                else:
                    self.score_rows[i].hide()
