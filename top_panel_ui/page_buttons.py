from soldat_extmod_api.graphics_helper.gui_addon import Button,\
                            BUTTON_HOVER_DEFAULT_COLOR, BUTTON_DEFAULT_COLOR,\
                            BUTTON_PRESSED_DEFAULT_COLOR
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D
from soldat_extmod_api.mod_api import ModAPI

from top_panel_ui.ui_top_constants import *


class PageButton(Button):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            image_path, 
            padding_x, 
            padding_y
        ):
        super().__init__(
            mod_api, parent, 
            padding_x, padding_y, 
            mod_api.create_interface_image(
                image_path,
                scale=PANEL_SCALE
            ), 
            True
        )
        self.press_callback = None

    def on_click(self, position: Vector2D):
        if self.contains_point(position):
            self.image.set_color(BUTTON_PRESSED_DEFAULT_COLOR)

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)
            self.press_callback()

    def on_cursor_enter(self):
        self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)
        self.image.set_color(BUTTON_HOVER_DEFAULT_COLOR)

    def on_cursor_exit(self):
        self.image.set_color(BUTTON_DEFAULT_COLOR)

    def set_pos(self, pos: Vector2D):
        pos += self.padding
        return super().set_pos(pos)

    def hide(self):
        self.image.hide()

    def show(self):
        self.image.show()


class PageUpButton(PageButton):
    def __init__(self, mod_api: ModAPI, parent, padding_x, padding_y):
        super().__init__(mod_api, parent, "mod_graphics/top_panel/page_up.png", padding_x, padding_y)

class PageDownButton(PageButton):
    def __init__(self, mod_api: ModAPI, parent, padding_x, padding_y):
        super().__init__(mod_api, parent, "mod_graphics/top_panel/page_down.png", padding_x, padding_y)
