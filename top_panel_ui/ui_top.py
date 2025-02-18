from soldat_extmod_api.graphics_helper.sm_text import CharacterSize, FontStyle, InterfaceText
from soldat_extmod_api.graphics_helper.color import WHITE, BLACK, Color
from soldat_extmod_api.graphics_helper.gui_addon import Container
from soldat_extmod_api.mod_api import ModAPI, Event

from top_panel_ui.page_buttons import PageDownButton, PageUpButton
from top_panel_ui.column_name_row import ColumnNameRow
from top_panel_ui.score_row import ScoreRow, Medal
from top_panel_ui.ui_top_constants import *
from top_panel_ui.panel_row import PanelRow

from info_provider.info_provider import InfoProvider

from replay_manager import ReplayManager
from map_manager import MapManager


class TopPanel(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            map_manager: MapManager,
            replay_manager: ReplayManager,
            padding_x: float, 
            padding_y: float,
            info_provider: InfoProvider):

        self.mod_api = mod_api
        self.map_manager = map_manager
        self.replay_manager = replay_manager
        self.last_top_data = {}
        super().__init__(
            mod_api.get_gui_frame(),
            padding_x,
            padding_y,
            self.mod_api.create_interface_image(
                "mod_graphics/top_panel/panel_back.png",
                scale=PANEL_SCALE
            )
        )
    
        self.info_provider = info_provider
        self.rows: list[ScoreRow] = []
        self.rows_start_vertical_padding = 95 * PANEL_SCALE.y
        self.title_text_scale = 2.1 * PANEL_SCALE.x
        self.map_text_scale = 4 * PANEL_SCALE.x
        self.title_text_pos = self.corner_top_left.add(Vector2D(108, 2))
        self.horizontal_center = self.position.add(
            Vector2D(self.dimensions.x / 2 * PANEL_SCALE.x, 45 * PANEL_SCALE.y)
        )
        self.map_name_text = CenteredText(
            self.mod_api, 
            "", 
            self.horizontal_center, 
            WHITE, 
            BLACK, 
            1, 
            Vector2D(self.map_text_scale, self.map_text_scale), 
            self.map_text_scale
        )
        self.top_panel_title = self.mod_api.create_interface_text(
            f"SCORES", 
            self.position + Vector2D(240 * PANEL_SCALE.x, 15 * PANEL_SCALE.y),
            WHITE, 
            BLACK,
            1, 
            Vector2D(self.title_text_scale, self.title_text_scale),
            FontStyle.FONT_WEAPONS_MENU, 
            self.title_text_scale
        )

        self.column_name_row = ColumnNameRow(self.mod_api, self)
        self.add_row(self.column_name_row)

        self.mod_api.subscribe_event(self.on_map_change, Event.MAP_CHANGE)
        self.mod_api.subscribe_event(self.on_join, Event.DIRECTX_READY)
        self.hidden = False
        self.page = 0
        self.top_page_change_callback = None

        self.init_rows()

        self.page_down_button = PageDownButton(self.mod_api, self, -1, -65)
        self.page_down_button.set_pos(self.corner_bottom_right)
        self.page_down_button.press_callback = self.on_page_down_pressed

        self.page_up_button = PageUpButton(self.mod_api, self, -1, 7)
        self.page_up_button.set_pos(self.corner_top_right)
        self.page_up_button.press_callback = self.on_page_up_pressed




    def init_rows(self):
        for i in range(10):
            if i < 3:
                row = ScoreRow(self.mod_api, self, self.info_provider, Medal._value2member_map_[i])
            else:
                row = ScoreRow(self.mod_api, self, self.info_provider, Medal._value2member_map_[3])
                row.set_place_text(i+1)
            self.add_row(row)

    def on_map_change(self, map_name: str):
        self.map_name_text.set_text(map_name)
        self.map_name_text.set_pos(self.horizontal_center)
        for row in self.rows:
            if isinstance(row, ScoreRow):
                row.replay_close_button.hide()
                row.replay_states.clear()

    def on_join(self):
        self.map_name_text.set_text(self.map_manager.current_map_name)
        self.map_name_text.set_pos(self.horizontal_center)

    def hide(self):
        self.hidden = True
        self.top_panel_title.hide()
        self.map_name_text.hide()
        self.image.hide()
        for row in self.rows:
            row.hide()
        self.page_down_button.hide()
        self.page_up_button.hide()
    
    def show(self):
        self.hidden = False
        self.top_panel_title.show()
        self.map_name_text.show()
        self.image.show()
        for row in self.rows:
            row.show()
        self.page_down_button.show()
        self.page_up_button.show()
        self.display_top_data(self.last_top_data)

    def add_row(self, row: 'PanelRow'):
        if self.rows:
            position = self.rows[-1].corner_bottom_left.add(Vector2D(0, ROW_VERTICAL_SPACING))
        else:
            position = row.position.add(Vector2D(0, self.rows_start_vertical_padding))
        row.set_pos(position)
        self.rows.append(row)

    def display_top_data(self, top_data: dict):
        self.last_top_data = top_data
        if not self.hidden:
            keys = list(top_data.keys()) if top_data else []
            entries_length = len(keys)
            for i in range(1,11): # starts at 2nd index because first index is occupied by column name row
                current_row = self.rows[i]
                if top_data:
                    if i > entries_length:
                        current_row.hide()
                    else:
                        current_row.show()
                        current_row.switch_top3_state(self.page == 0)
                        current_row.replay_id = top_data[keys[i-1]]["replay_id"]
                        if current_row.replay_id in self.replay_manager.bots:
                            current_row.replay_close_button.show()
                        else:
                            current_row.replay_close_button.hide()
                        if current_row.get_replay_state(current_row.replay_id):
                            current_row.replay_button.play()
                        else:
                            current_row.replay_button.pause()
                        current_row.set_place_text(i+(self.page * 10))
                        current_row.set_username(keys[i-1])
                        current_row.set_record_time(top_data[keys[i-1]]["record_time"])
                else:
                    current_row.hide()

    def on_page_down_pressed(self):
        self.page += 1
        self.top_page_change_callback()

    def on_page_up_pressed(self):
        if self.page - 1 >= 0:
            self.page -= 1
            self.top_page_change_callback()

class CenteredText(InterfaceText):
    def __init__(
        self, 
        mod_api, 
        text: str, 
        position: Vector2D, 
        color: Color, 
        shadow_color: Color, 
        scale: float, 
        shadow_scale: Vector2D, 
        font_scale: float
    ):
        super().__init__(
            mod_api, 
            text, 
            position, 
            color, 
            shadow_color, 
            scale, 
            shadow_scale, 
            FontStyle.FONT_WEAPONS_MENU, 
            font_scale
        )
        self.text_center_offset = Vector2D(
            len(text) * (CharacterSize.FONT_WEAPONS_MENU * scale), 
            0
        )

    def set_pos(self, pos: Vector2D):
        pos = pos.sub(self.text_center_offset)
        return super().set_pos(pos)

    def set_text(self, text: str):
        super().set_text(text)
        self.text_center_offset = Vector2D(
            len(text) * (CharacterSize.FONT_WEAPONS_MENU * self.scale), 
            0
        )

