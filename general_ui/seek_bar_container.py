from soldat_extmod_api.graphics_helper.gui_addon import Container
from soldat_extmod_api.mod_api import ModAPI, Vector2D, Color

from general_ui.replay_seek_bar import ReplaySeekBar, TimestampText
from general_ui.seek_bar_button import SeekBarButton
from collections.abc import Callable


class SeekBarContainer(Container):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float,
            pause_callback: Callable,
            play_callback: Callable
        ):
        self.time_stamp_current = TimestampText(
            mod_api,
            mod_api.get_gui_frame(),
            0,
            0,
            0,
            0
        )
        self.time_stamp_end = TimestampText(
            mod_api,
            mod_api.get_gui_frame(),
            0,
            0,
            0,
            0
        )
        super().__init__(
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "mod_graphics/slider_back.png",
                scale=Vector2D(0.5, 0.5),
                color=Color.from_hex("161821ff")
            ), 
            True
        )
        self.hidden = False
        self.mod_api = mod_api
        self.replay_seek_bar = ReplaySeekBar(self.mod_api, self, 0, 0, True)
        self.replay_seek_bar.image.set_color(Color.from_hex("494e69ff"))
        self.replay_seek_bar.slider_filled.set_color(Color.from_hex("191b24ff"))
        time_stamps_spacing_y = 2
        button_spacing = 1
        time_stamp_current_pos = Vector2D(0, self.time_stamp_current.dimensions.y * self.time_stamp_current.scale.y)
        time_stamp_current_pos = self.corner_top_left - time_stamp_current_pos
        self.time_stamp_current.set_pos(time_stamp_current_pos - Vector2D(0, time_stamps_spacing_y))
        self.time_stamp_current.update_text("00:00:00:000")
        self.time_stamp_current.text.set_pos(time_stamp_current_pos)

        time_stamp_end_pos = Vector2D(0, self.time_stamp_end.dimensions.y * self.time_stamp_end.scale.y)
        time_stamp_end_pos = self.corner_top_right - time_stamp_end_pos

        time_stamp_end_pos = time_stamp_end_pos - Vector2D(
            self.time_stamp_end.scale.x * self.time_stamp_end.dimensions.x, 0)

        self.time_stamp_end.set_pos(time_stamp_end_pos - Vector2D(0, time_stamps_spacing_y))
        self.time_stamp_end.update_text("00:00:00:000")
        self.time_stamp_end.text.set_pos(time_stamp_end_pos)

        self.seek_bar_button = SeekBarButton(self.mod_api, self, 0, 0, pause_callback, play_callback)
        seek_bar_button_size_x = self.seek_bar_button.corner_top_right.x - self.seek_bar_button.corner_top_left.x
        seek_bar_button_pos = self.seek_bar_button.position - Vector2D(seek_bar_button_size_x + button_spacing, 0)
        self.seek_bar_button.set_pos(seek_bar_button_pos)

    def hide(self):
        self.image.hide()
        self.seek_bar_button.hide()
        self.time_stamp_current.text.hide()
        self.time_stamp_end.text.hide()
        self.time_stamp_current.image.hide()
        self.time_stamp_end.image.hide()
        self.replay_seek_bar.hide()

    def show(self):
        self.image.show()
        self.seek_bar_button.show()
        self.time_stamp_current.text.show()
        self.time_stamp_end.text.show()
        self.time_stamp_current.image.show()
        self.time_stamp_end.image.show()
        self.replay_seek_bar.show()
