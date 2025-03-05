from soldat_extmod_api.graphics_helper.gui_addon import PauseButton
from soldat_extmod_api.mod_api import ModAPI, Vector2D
from collections.abc import Callable


class SeekBarButton(PauseButton):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float,
            pause_callback: Callable,
            play_callback: Callable
        ):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "mod_graphics/button_playing.png",
                scale=Vector2D(0.5, 0.5)
            ), 
             mod_api.create_interface_image(
                "mod_graphics/button_paused.png",
                scale=Vector2D(0.5, 0.5)
            ), 
            False
        )
        self.hidden = False
        self.callback = {True: pause_callback, False: play_callback}
        self.pause_callback = pause_callback
        self.play_callback = play_callback

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "image_paused"):
            self.image_paused.set_pos(pos)
        return super().set_pos(pos)

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

    def on_mouse_release(self, position: Vector2D):
        contains = super().on_mouse_release(position)
        if contains:
            self.callback[self.paused]()
        return contains
