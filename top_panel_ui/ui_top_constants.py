from soldat_extmod_api.mod_api import Vector2D, Color
from enum import Enum

PANEL_SCALE = Vector2D(0.4, 0.4)
PANEL_OUTLINE_SIZE = Vector2D(7 * PANEL_SCALE.x, 7 * PANEL_SCALE.y)
ROW_VERTICAL_SPACING = 0
USERNAME_WRAPPING_LENGTH = 13

class MedalColor(Enum):
    GOLD = Color.from_hex("fcf305ff")
    SILVER = Color.from_hex("c3c2c3ff")
    BRONZE = Color.from_hex("f6a050ff")

class Medal(Enum):
    GOLD = 0
    SILVER = 1
    BRONZE = 2
    NONE = 3

medal_color_mapping = {
    Medal.GOLD: MedalColor.GOLD.value,
    Medal.SILVER: MedalColor.SILVER.value,
    Medal.BRONZE: MedalColor.BRONZE.value
}
