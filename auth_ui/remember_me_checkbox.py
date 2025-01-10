from soldat_extmod_api.graphics_helper.gui_addon import Checkbox
from soldat_extmod_api.mod_api import Vector2D, ModAPI, Color, FontStyle, BLACK, WHITE


class RemembermeCheckbox(Checkbox):
    def __init__(self, parent, padding_x: float, padding_y: float):
        self.mod_api: ModAPI = parent.mod_api
        checkbox_image = self.mod_api.create_interface_image(
            "mod_graphics/checkbox.png", 
            scale=Vector2D(0.5, 0.5)
        )
        super().__init__(self.mod_api, parent, padding_x, padding_y, checkbox_image, False)

        self.checkbox_outline = self.mod_api.create_interface_image(
            "mod_graphics/checkbox_outline.png", 
            self.position.sub(Vector2D(1, 1)), 
            scale=Vector2D(0.5, 0.5), 
            color=Color.from_bytes(b"\x63\x63\x63\xFF")
        )
        self.text = self.mod_api.create_interface_text(
            "Remember me", 
            self.position.add(Vector2D((self.image.get_dimensions.x * self.scale.x) + 2, 2.3)), 
            BLACK, 
            WHITE, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_SMALLEST, 
            1.3
        )

# Overrides  ----------------------------------- 
    def hide(self):
        self.image.hide()
        self.text.hide()
        self.checkbox_outline.hide()
        self.unsubscribe()

    def show(self):
        self.image.show()
        self.text.show()
        self.checkbox_outline.show()
        self.subscribe()
