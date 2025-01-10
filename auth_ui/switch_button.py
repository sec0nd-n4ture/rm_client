from soldat_extmod_api.graphics_helper.gui_addon import Button
from soldat_extmod_api.mod_api import ModAPI, Vector2D, FontStyle, Color, WHITE, BLACK


class SwitchButton(Button):
    def __init__(self, parent, top_level_container, padding_x: float, padding_y: float):
        self.mod_api: ModAPI = top_level_container.mod_api
        self.top_level_container = top_level_container
        self.button_shadow_image = self.mod_api.create_interface_image(
            "mod_graphics/auth_button_shadow.png", 
            scale=Vector2D(0.25, 0.3)
        )
        button_back_image = self.mod_api.create_interface_image(
            "mod_graphics/auth_button.png", 
            scale=Vector2D(0.25, 0.3)
        )

        super().__init__(
            self.mod_api, 
            parent, 
            padding_x, 
            padding_y, 
            button_back_image, 
            False
        )

        self.button_shadow_image.set_pos(self.position.sub(Vector2D(10.5 * 0.25, 2 * 0.3)))
        self.button_text = self.mod_api.create_interface_text(
            "Register", 
            self.position.add(Vector2D(5, 2.4)), 
            WHITE, 
            BLACK, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_MENU, 
            0.73
        )

        self.info_text = self.mod_api.create_interface_text(
            "Don't have an account?", 
            parent.position.add(Vector2D(-28, padding_y + 6)), 
            BLACK, 
            WHITE, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_SMALLEST, 
            0.9
        
        )
        self.icon_image = self.mod_api.create_interface_image(
            "mod_graphics/fa-arrow-right-solid.png", 
            scale=Vector2D(0.5, 0.5), 
            color=WHITE
        )
        self.icon_image.set_pos(
            self.corner_top_right.sub(
                Vector2D((self.icon_image.get_dimensions.x * 0.5) + 4, -5)
            )
        )
        self.color_normal = Color.from_bytes(b"\x0e\x0e\x0e\xff")
        self.color_hover = Color.from_bytes(b"\x4b\x4b\x4b\xff")
        self.color_pressed = Color.from_bytes(b"\x8e\x8e\x8e\xff")
        self.image.set_color(self.color_normal)
        self.switched = False


# Overrides  ----------------------------------- 
    def hide(self):
        self.button_shadow_image.hide()
        self.image.hide()
        self.button_text.hide()
        self.info_text.hide()
        self.icon_image.hide()
        self.unsubscribe()

    def show(self):
        self.button_shadow_image.show()
        self.image.show()
        self.button_text.show()
        self.info_text.show()
        self.icon_image.show()
        self.subscribe()

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.image.set_color(self.color_hover)
            self.switch()

    def on_click(self, position: Vector2D):
        if self.contains_point(position):
            self.image.set_color(self.color_pressed)

    def on_hover(self, position: Vector2D):
        return super().on_hover(position)

    def on_cursor_enter(self):
        self.image.set_color(self.color_hover)

    def on_cursor_exit(self):
        self.image.set_color(self.color_normal)
# ----------------------------------------------------------------------

    def switch(self):
        self.switched ^= 1
        auth_container = self.top_level_container
        if self.switched:
            self.info_text.set_text("Already registered?")
            auth_container.confirm_field.show()
            auth_container.title_text.set_text("Register")
            auth_container.title_text.set_pos(auth_container.title_text.text_position.sub(Vector2D(22, 0)))
            auth_container.submit_button.text.set_pos(auth_container.submit_button.text.text_position.sub(Vector2D(11, 0)))
            auth_container.submit_button.text.set_text("Register")
            self.button_text.set_text("Login")
        else:
            self.info_text.set_text("Don't have an account?")
            auth_container.confirm_field.hide()
            auth_container.submit_button.text.set_text("Login")
            auth_container.submit_button.text.set_pos(auth_container.submit_button.text.text_position.add(Vector2D(11, 0)))
            auth_container.title_text.set_pos(auth_container.title_text.text_position.add(Vector2D(22, 0)))
            auth_container.title_text.set_text("Login")
            self.button_text.set_text("Register")

