from soldat_extmod_api.mod_api import WHITE, BLACK, FontStyle, ModAPI
from soldat_extmod_api.graphics_helper.gui_addon import UIElement
from top_panel_ui.panel_row import PanelRow
from top_panel_ui.ui_top_constants import *


class ColumnNameRow(PanelRow):
    def __init__(self, mod_api: ModAPI, parent: UIElement):
        self.text_scale = 2.3 * PANEL_SCALE.x
        self.col_name_text = mod_api.create_interface_text(
            f"    NAME      TIME     DATE", Vector2D.zero(),
            WHITE, BLACK,
            1, Vector2D(self.text_scale, self.text_scale),
            FontStyle.FONT_WEAPONS_MENU, self.text_scale
        )
        super().__init__(mod_api, parent)

    def set_pos(self, pos: Vector2D):
        super().set_pos(pos)
        self.col_name_text.set_pos(self.position.add(Vector2D(0, 14 * PANEL_SCALE.x)))

    def hide(self):
        self.image.hide()
        self.col_name_text.hide()

    def show(self):
        self.image.show()
        self.col_name_text.show()
