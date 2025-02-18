from soldat_extmod_api.mod_api import ModAPI, FontStyle, WHITE, BLACK, Color
from soldat_extmod_api.graphics_helper.gui_addon import UIElement

from top_panel_ui.replay_button import ReplayButton, ReplayCloseButton
from top_panel_ui.panel_row import PanelRow
from top_panel_ui.ui_top_constants import *

from info_provider.info_provider import InfoProvider
from replay_manager import ReplayManager
from jobs import AddReplaybotJob

def medal_only_method(func):
    def wrapper(self, *args):
        if self.medal != Medal.NONE:
            return func(self, *args)
        else:
            pass
    return wrapper

class ScoreRow(PanelRow):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent: UIElement, 
            info_provider: InfoProvider,
            medal: Medal = None
        ):
        super().__init__(mod_api, parent)
        self.info_provider = info_provider
        self.medal = medal
        self.place = None
        self.replay_id = None
        self.replay_manager: ReplayManager = parent.replay_manager
        self.replay_states: dict[int, bool] = {}
        if self.medal != Medal.NONE:
            self.row_gradient_image = mod_api.create_interface_image(
                "./mod_graphics/top_panel/row_gradient.png", 
                scale=PANEL_SCALE
            )
            match self.medal.value:
                case Medal.GOLD.value:
                    medal_image_file = "./mod_graphics/top_panel/gold_medal.png"
                case Medal.SILVER.value:
                    medal_image_file = "./mod_graphics/top_panel/silver_medal.png"
                case Medal.BRONZE.value:
                    medal_image_file = "./mod_graphics/top_panel/bronze_medal.png"

            self.set_gradient_color(medal_color_mapping.get(medal))
            self.medal_image = mod_api.create_interface_image(
                medal_image_file, 
                scale=PANEL_SCALE
            )

        self.nth_text = mod_api.create_interface_text(
            "", 
            Vector2D.zero(),
            WHITE, 
            BLACK, 
            1, 
            Vector2D(0.4, 0.8), 
            FontStyle.FONT_SMALL_BOLD, 
            0.4
        )
        self.username_text_scale = 1.7 * PANEL_SCALE.x
        self.date_text_scale = 1.2 * PANEL_SCALE.x
        self.time_text_scale = 1.5 * PANEL_SCALE.x
        self.username_text = mod_api.create_interface_text(
            "", 
            Vector2D.zero(), 
            WHITE, 
            BLACK, 
            1, 
            Vector2D(self.username_text_scale, self.username_text_scale), 
            FontStyle.FONT_SMALL, 
            self.username_text_scale
        )
        self.username = ""
        self.time_column_back = mod_api.create_interface_image(
            "./mod_graphics/top_panel/time_column_back.png",
            scale=PANEL_SCALE
        )
        self.date_text = mod_api.create_interface_text(
            "", 
            Vector2D.zero(), 
            WHITE, 
            BLACK, 
            1, 
            Vector2D(self.date_text_scale, self.date_text_scale), 
            FontStyle.FONT_SMALL, 
            self.date_text_scale
        )
        self.time_text = mod_api.create_interface_text(
            "", 
            Vector2D.zero(), 
            Color.from_hex("00F0FFFF"), 
            BLACK, 
            1, 
            Vector2D(self.time_text_scale, self.time_text_scale), 
            FontStyle.FONT_SMALL, 
            self.time_text_scale
        )
        self.replay_button = ReplayButton(
            self.mod_api,
            self,
            0,
            0,
            self.pause_callback,
            self.play_callback
        )
        self.replay_close_button = ReplayCloseButton(
            self.mod_api,
            self,
            -5,
            0,
            self.replay_close_callback
        )
        self.replay_close_button.hide()
        self.is_first_page = False

    def play_callback(self):
        if self.replay_id in self.replay_manager.bots:
            self.replay_manager.bots[self.replay_id].play()
        else:
            medal = self.medal if self.is_first_page else Medal.NONE
            self.info_provider.submit_job(
                AddReplaybotJob(
                    self.replay_manager,
                    medal,
                    self.replay_id
                )
            )
        self.replay_states[self.replay_id] = True
        self.replay_close_button.show()

    def pause_callback(self):
        if self.replay_id in self.replay_manager.bots:
            self.replay_manager.bots[self.replay_id].pause()
            self.replay_states[self.replay_id] = False

    def replay_close_callback(self):
        if self.replay_id in self.replay_manager.bots:
            self.replay_states.pop(self.replay_id)
            self.replay_button.pause()
            bot = self.replay_manager.bots[self.replay_id]
            self.replay_manager.bots.pop(self.replay_id)
            del bot
            self.replay_close_button.hide()

    @medal_only_method
    def set_gradient_color(self, color: Color):
        self.row_gradient_image.set_color(color)

    @medal_only_method
    def show_gradient(self):
        self.row_gradient_image.show()

    def hide_gradient(self):
        self.row_gradient_image.hide()

    def hide_place_text(self):
        self.nth_text.hide()
    
    def set_username(self, username: str):
        username_len = len(username)
        wrapped = False
        if username_len > USERNAME_WRAPPING_LENGTH:
            wrapped = True
            username = username[:USERNAME_WRAPPING_LENGTH] + "\r\n" + username[USERNAME_WRAPPING_LENGTH:username_len]
        self.username_text.set_text(username)
        self.username = username
        self.username_text.set_pos(
            self.position.add(Vector2D(50 * PANEL_SCALE.x, (15 - (int(wrapped) * 13)) * PANEL_SCALE.y))
        )

    def set_record_time(self, time: float):
        self.time_text.set_text(str(time))

    def set_place_text(self, place: int):
        self.nth_text.set_text(f"{str(place)}th")
        self.place = place

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "row_gradient_image"):
            self.row_gradient_image.set_pos(pos)
        if hasattr(self, "nth_text"):
            self.nth_text.set_pos(pos.add(Vector2D(4 * PANEL_SCALE.x, 20 * PANEL_SCALE.y)))
        if hasattr(self, "medal_image"):
            self.medal_image.set_pos(pos.add(Vector2D(4 * PANEL_SCALE.x, 10 * PANEL_SCALE.y)))
        if hasattr(self, "time_column_back"):
            self.time_column_back.set_pos(pos.add(Vector2D(250 * PANEL_SCALE.x , 9 * PANEL_SCALE.y)))
        super().set_pos(pos)
        if hasattr(self, "username_text"):
            self.username_text.set_pos(pos.add(Vector2D(50 * PANEL_SCALE.x, 15 * PANEL_SCALE.y)))
        if hasattr(self, "date_text"):
            self.date_text.set_pos(pos.add(Vector2D(410 * PANEL_SCALE.x , 20 * PANEL_SCALE.y)))
        if hasattr(self, "time_text"):
            self.time_text.set_pos(pos.add(Vector2D(280 * PANEL_SCALE.x , 20 * PANEL_SCALE.y)))
        if hasattr(self, "replay_button"):
            self.replay_button.set_pos(self.corner_top_right.sub(Vector2D(20, -1.5)))
        if hasattr(self, "replay_close_button"):
            self.replay_close_button.set_pos(self.corner_top_right.add(self.replay_close_button.padding))

    @medal_only_method
    def switch_top3_state(self, is_first_page: bool):
        self.is_first_page = is_first_page
        if is_first_page:
            self.show_gradient()
            self.nth_text.hide()
            self.medal_image.show()
        else:
            self.hide_gradient()
            self.nth_text.show()
            self.medal_image.hide()

    def get_replay_state(self, replay_id: int) -> bool:
        if replay_id in self.replay_states:
            return self.replay_states[replay_id]

    def hide(self):
        self.image.hide()
        if self.medal != Medal.NONE:
            self.row_gradient_image.hide()
            self.medal_image.hide()
        self.nth_text.hide()
        self.time_column_back.hide()
        self.username_text.hide()
        self.date_text.hide()
        self.time_text.hide()
        self.replay_button.hide()
        self.replay_close_button.hide()

    def show(self):
        self.image.show()
        if self.medal == Medal.NONE:
            self.nth_text.show()
        elif self.is_first_page:
            self.row_gradient_image.show()
            self.medal_image.show()
        else:
            self.nth_text.show()
        self.time_column_back.show()
        self.username_text.show()
        self.date_text.show()
        self.time_text.show()
        self.replay_button.show()
        if self.replay_id in self.replay_manager.bots:
            self.replay_close_button.show()
