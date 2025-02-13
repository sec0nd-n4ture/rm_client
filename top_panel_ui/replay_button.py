from soldat_extmod_api.graphics_helper.gui_addon import PauseButton, Button,\
                            BUTTON_HOVER_DEFAULT_COLOR, BUTTON_DEFAULT_COLOR,\
                            BUTTON_PRESSED_DEFAULT_COLOR
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D
from soldat_extmod_api.mod_api import ModAPI
from top_panel_ui.ui_top_constants import *


class ReplayButton(PauseButton):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float, 
            pause_callback, 
            play_callback
        ):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "./mod_graphics/top_panel/button_playing.png", 
                scale=Vector2D(PANEL_SCALE.x, PANEL_SCALE.x)
            ), 
            mod_api.create_interface_image(
                "./mod_graphics/top_panel/button_paused.png", 
                scale=Vector2D(PANEL_SCALE.x, PANEL_SCALE.x)
            ), 
            True
        )
        self.callback = {True: pause_callback, False: play_callback}
        self.pause_callback = pause_callback
        self.play_callback = play_callback
        self.hidden = False


    def on_mouse_release(self, position: Vector2D):
        contains_pos = super().on_mouse_release(position)
        if contains_pos:
            self.callback[self.paused]()
        return contains_pos

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.unsubscribe()
            return super().hide()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.subscribe()
            return super().show()

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "image_paused"):
            self.image_paused.set_pos(pos)
        return super().set_pos(pos)

class ReplayCloseButton(Button):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float, 
            close_callback):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "./mod_graphics/top_panel/button_close.png", 
                scale=Vector2D(PANEL_SCALE.x - 0.17, PANEL_SCALE.x - 0.17)
            ), 
            False
        )
        self.close_callback = close_callback
        self.hidden = False

    def on_click(self, position: Vector2D):
        if self.contains_point(position):
            self.image.set_color(BUTTON_PRESSED_DEFAULT_COLOR)

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)
            self.close_callback()

    def on_cursor_enter(self):
        self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)
        self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)

    def on_cursor_exit(self):
        self.image.set_color(BUTTON_DEFAULT_COLOR)

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.image.hide()
            self.unsubscribe()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.image.show()
            self.subscribe()

