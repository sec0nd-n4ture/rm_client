from soldat_extmod_api.graphics_helper.gui_addon import UIElement
from soldat_extmod_api.mod_api import ModAPI
from top_panel_ui.ui_top_constants import *

class PanelRow(UIElement):
    def __init__(self, mod_api: ModAPI, parent: UIElement):
        row_image = mod_api.create_interface_image(
            "./mod_graphics/top_panel/row.png",
            scale=PANEL_SCALE
        )
        super().__init__(parent, PANEL_OUTLINE_SIZE.x, 0, row_image, False)
        self.mod_api = mod_api
