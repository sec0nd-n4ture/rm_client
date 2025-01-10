from soldat_extmod_api.mod_api import ModAPI, Vector2D, FontStyle, WHITE, BLACK, RED 
from soldat_extmod_api.graphics_helper.gui_addon import Container

from db_client.db_client import DBClient
from auth_ui.auth_label import AuthLabel
from auth_ui.remember_me_checkbox import RemembermeCheckbox
from auth_ui.submit_button import SubmitButton
from auth_ui.switch_button import SwitchButton

class AuthContainer(Container):
    def __init__(self, mod_api: ModAPI, db_client: DBClient):
        self.mod_api = mod_api
        self.db_client = db_client
        self.mod_api.take_camera_controls()
        self.mod_api.take_cursor_controls()
        register_back_image = mod_api.create_interface_image(
            "mod_graphics/reg_ui_back.png", 
            scale=Vector2D(0.5, 0.5)
        )
        super().__init__(mod_api.get_gui_frame(), 0, 0, register_back_image, True)
        self.children = []
        self.title_text = self.mod_api.create_interface_text(
            "Login",
            Vector2D(self.position.x + 95, self.position.y + 3),
            WHITE,
            BLACK,
            1,
            Vector2D(2.3, 3.3),
            FontStyle.FONT_MENU,
            1.3
        )
        self.children.append(self.title_text)
        self.username_field = AuthLabel(
            self,
            self,
            22,
            60,
            "fa-user",
            "Username",
            27
        )
        self.children.append(self.username_field)
        self.password_field = AuthLabel(
            self.username_field,
            self,
            0,
            25,
            "fa-lock",
            "Password",
            27
        )
        self.children.append(self.password_field)
        self.confirm_field = AuthLabel(
            self.password_field, 
            self,
            0, 
            25, 
            "fa-lock", 
            "Confirm password", 
            27
        )
        self.children.append(self.confirm_field)
        self.admin_password_field = AuthLabel(
            self.confirm_field, 
            self,
            0, 
            25, 
            "fa-lock", 
            "Admin password", 
            27)

        self.admin_password_field.hide()
        self.children.append(self.admin_password_field)
        self.password_field.passwordfield = True
        self.admin_password_field.passwordfield = True
        self.confirm_field.passwordfield = True
        self.checkbox = RemembermeCheckbox(self.confirm_field, 0, 65)
        self.children.append(self.checkbox)
        self.submit_button = SubmitButton(self.checkbox, self, 18, 17)
        self.children.append(self.submit_button)
        self.switch_button = SwitchButton(self.submit_button, self, 125, 60)
        self.children.append(self.switch_button)
        self.hidden = False
        self.confirm_field.hide()
        self.auth_status_text = self.mod_api.create_interface_text(
            "", 
            self.confirm_field.position.add(Vector2D(0, 27)),
            RED, 
            WHITE, 
            1, 
            Vector2D.zero(), 
            FontStyle.FONT_SMALLEST, 
            0.8
        )
        self.children.append(self.auth_status_text)
        self.auth_status_text.hide()

    def hide(self):
        self.image.hide()
        for child in self.children:
            child.hide()
        self.hidden = True
        self.__show_chat()
        self.camera_controls.restore_camera_controls()
        self.camera_controls.restore_cursor_controls()

    def show(self):
        self.image.show()
        self.hidden = False
        for child in self.children:
            child.show()

    def __show_chat(self):
        self.mod_api.soldat_bridge.write(
            self.mod_api.addresses["chat_show_flag"],
            b"\x00"
        )
