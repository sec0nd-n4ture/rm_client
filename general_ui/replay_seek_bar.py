from soldat_extmod_api.graphics_helper.gui_addon import \
    SliderBar, SliderKnob, TextLabel
from soldat_extmod_api.graphics_helper.color import WHITE, BLACK, Color
from soldat_extmod_api.mod_api import ModAPI, Vector2D, FontStyle


class ReplaySeekBar(SliderBar):
    def __init__(
            self, 
            mod_api: ModAPI, 
            parent, 
            padding_x: float, 
            padding_y: float,
            centered: bool = True
        ):
        super().__init__(
            mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            mod_api.create_interface_image(
                "mod_graphics/slider.png",
                scale=Vector2D(0.5, 0.5),
            ), 
            mod_api.create_interface_image(
                "mod_graphics/slider.png",
                scale=Vector2D(0.5, 0.5)
            ), 
            centered
        )
        self.knob = SliderKnob(
            self, 
            0, 
            -2.5,
            mod_api.create_interface_image(
                "mod_graphics/slider_knob.png",
                scale=Vector2D(0.5, 0.5)
            ), 
            0
        )
        self.hidden = False

    def hide(self):
        if not self.hidden:
            self.hidden = True
            self.knob.image.hide()
            self.image.hide()
            self.slider_filled.hide()
            self.unsubscribe()

    def show(self):
        if self.hidden:
            self.hidden = False
            self.knob.image.show()
            self.image.show()
            self.slider_filled.show()
            self.subscribe()


class TimestampText(TextLabel):
    def __init__(
            self, 
            mod_api: ModAPI,
            parent, 
            padding_x: float, 
            padding_y: float, 
            text_padding_x: float, 
            text_padding_y: float
        ):
        super().__init__(
            parent, 
            mod_api.create_interface_text(
                "",
                Vector2D.zero(),
                WHITE,
                BLACK,
                1,
                Vector2D(1, 2),
                FontStyle.FONT_SMALL,
                0.5
            ), 
            padding_x, 
            padding_y, 
            text_padding_x, 
            text_padding_y, 
            mod_api.create_interface_image(
                "mod_graphics/text_back.png",
                scale=Vector2D(1.65, 0.5),
                color=Color(0,0,0, "50%")
            )
        )
