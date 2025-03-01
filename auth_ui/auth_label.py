from soldat_extmod_api.mod_api import ModAPI, Vector2D, Color, FontStyle, WHITE, BLACK
from soldat_extmod_api.graphics_helper.gui_addon import TextField, UIElement
from pynput.keyboard import Key, KeyCode


class AuthLabel(TextField):
    def __init__(
        self,
        parent: UIElement, 
        top_level_container,
        padding_x: float, 
        padding_y: float, 
        icon_name: str, 
        label_text: str, 
        max_text: int = 4096,
    ):
        self.top_level_container = top_level_container
        self.mod_api: ModAPI = top_level_container.mod_api
        ifaceimg_txtback = self.mod_api.create_interface_image(
            "mod_graphics/text_field_back.png", 
            parent.position, 
            parent.scale, 
            color=Color.from_bytes(b"\xcd\xcd\xcd\xff")
        )

        input_uitext = self.mod_api.create_interface_text(
            "", 
            parent.position, 
            BLACK, 
            WHITE, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_SMALLEST, 
            1
        )

        icon_padding_x = 5

        match icon_name:
            case "fa-user":
                icon_path = "mod_graphics/fa-user-solid.png"
            case "fa-lock":
                icon_path = "mod_graphics/fa-lock-solid.png"

        self.icon_image = self.mod_api.create_interface_image(
            icon_path, 
            scale=Vector2D(0.5, 0.5), 
            color=Color.from_bytes(b"\x62\x62\x62\xFF")
        )

        super().__init__(
            self.mod_api,
            parent, 
            input_uitext, 
            padding_x, 
            padding_y, 
            (self.icon_image.get_dimensions.x * parent.scale.x) + icon_padding_x, 
            1, 
            ifaceimg_txtback, 
            max_text
        )

        self.outline = self.mod_api.create_interface_image(
            "mod_graphics/text_field_back_outline.png", 
            Vector2D(self.position.x - 1, self.position.y - 1), 
            parent.scale, 
            color=Color.from_bytes(b"\xa0\xa0\xa0\xff")
        )

        self.icon_image.set_pos(self.position.add(Vector2D(5, 3)))
        self.label_uitext = self.mod_api.create_interface_text(
            label_text, 
            self.position.sub(Vector2D(0, 12)), 
            BLACK, 
            WHITE, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_WEAPONS_MENU, 
            1
        )
        self.focused = False
        self.hidden = False
        self.passwordfield = False
        self.true_text = ""

# Overrides  ----------------------------------- 
    def __handle_on_mup(self, pos: Vector2D):
        if not self.hidden:
            self.is_writing = self.contains_point(pos)
            if self.is_writing:
                self.cursor_position = len(self.input_text)
                self.outline.set_color(BLACK)
                self.focused = True
                self.__show_chat()
                self.update_text(self.input_text, True)
            else:
                self.outline.set_color(Color.from_bytes(b"\xa0\xa0\xa0\xff"))
                self.update_text(self.input_text, False)
                if self.focused:
                    others_focused = False
                    for child in self.top_level_container.children:
                        if isinstance(child, AuthLabel) and child != self:
                            if child.focused:
                                others_focused = True
                                break
                    if not others_focused:
                        self.__hide_chat()
                    self.focused = False

    def on_anykbkey_down(self, key):
        if hasattr(self, "passwordfield"):
            if not self.passwordfield:
                return super().on_anykbkey_down(key)
            if self.is_writing:
                if isinstance(key, KeyCode):
                    if len(self.input_text) < self.max_text:
                        self.input_text = self.input_text[:self.cursor_position] + "*" + self.input_text[self.cursor_position:]
                        self.true_text += key.char
                        self.cursor_position += 1
                    self.update_text(self.input_text)
                elif key == Key.backspace:
                    if self.cursor_position > 0:
                        self.input_text = self.input_text[:self.cursor_position - 1] + self.input_text[self.cursor_position:]
                        self.true_text = self.true_text[:self.cursor_position - 1] + self.true_text[self.cursor_position:]
                        self.cursor_position -= 1
                        self.update_text(self.input_text)

    def on_mouse_release(self, position: Vector2D):
        self.__handle_on_mup(position)

    def hide(self):
        self.image.hide()
        self.text.hide()
        self.label_uitext.hide()
        self.outline.hide()
        self.icon_image.hide()
        self.hidden = True
        self.unsubscribe()

    def show(self):
        self.image.show()
        self.text.show()
        self.label_uitext.show()
        self.outline.show()
        self.icon_image.show()
        self.hidden = False
        self.subscribe()

# Helpers -----------------------------------
    def __hide_chat(self):
        self.mod_api.soldat_bridge.write(self.mod_api.addresses["chat_show_flag"], b"\x00")

    def __show_chat(self):
        self.mod_api.soldat_bridge.write(self.mod_api.addresses["chat_show_flag"], b"\x01")
