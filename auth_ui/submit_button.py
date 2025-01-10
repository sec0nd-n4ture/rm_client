from soldat_extmod_api.graphics_helper.gui_addon import Button
from soldat_extmod_api.mod_api import ModAPI, Color, FontStyle, Vector2D, WHITE, BLACK


class SubmitButton(Button):
    def __init__(self, parent, top_level_container, padding_x: float, padding_y: float):
        self.mod_api: ModAPI = top_level_container.mod_api
        self.top_level_container = top_level_container
        self.button_shadow_image = self.mod_api.create_interface_image(
            "mod_graphics/auth_button_shadow.png", 
            scale=Vector2D(0.5, 0.5)
        )
        button_back_image = self.mod_api.create_interface_image(
            "mod_graphics/auth_button.png", 
            scale=Vector2D(0.5, 0.5)
        )
        super().__init__(
            self.mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            button_back_image, 
            False
        )

        self.button_shadow_image.set_pos(self.position.sub(Vector2D(5, 2)))
        self.color_normal = Color.from_bytes(b"\x0e\x0e\x0e\xff")
        self.color_hover = Color.from_bytes(b"\x4b\x4b\x4b\xff")
        self.color_pressed = Color.from_bytes(b"\x8e\x8e\x8e\xff")
        self.image.set_color(self.color_normal)

        self.text = self.mod_api.create_interface_text(
            "Login", 
            self.position.add(Vector2D(55, 5)), 
            WHITE, 
            BLACK, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_BIG, 
            1
        )

        self.clickable = True


# Overrides  ----------------------------------- 
    def on_click(self, position: Vector2D):
        if self.clickable:
            if self.contains_point(position):
                self.image.set_color(self.color_pressed)

    def on_mouse_release(self, position: Vector2D):
        if self.clickable:
            if self.contains_point(position):
                self.image.set_color(self.color_hover)
                self.clickable = False
                self.top_level_container.submit()

    def on_hover(self, position: Vector2D):
        return super().on_hover(position)

    def on_cursor_enter(self):
        self.image.set_color(self.color_hover)

    def on_cursor_exit(self):
        self.image.set_color(self.color_normal)

    def hide(self):
        self.button_shadow_image.hide()
        self.image.hide()
        self.text.hide()
        self.unsubscribe()

    def show(self):
        self.button_shadow_image.show()
        self.image.show()
        self.text.show()
        self.subscribe()
