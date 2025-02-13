from soldat_extmod_api.graphics_helper.gui_addon import ImageNode, Interactive, Rectangle
from soldat_extmod_api.mod_api import Vector2D, Vector3D
from checkpoint_container import CheckPointContainer
from soldat_extmod_api.graphics_helper.sm_text import FontStyle
from soldat_extmod_api.graphics_helper.color import Color, GREEN, RED
from soldat_extmod_api.mod_api import ModAPI, Event


class CheckPoint(ImageNode, Interactive, Rectangle):

    def __new__(
            cls, 
            position: Vector2D, 
            scale: Vector2D, 
            color: Color, 
            number: int, 
            mod_api: ModAPI):
        checkpoint = CheckPointContainer.get_checkpoint(number)
        if checkpoint is not None:
            return checkpoint
        return super().__new__(cls)
    
    def __init__(
            self, 
            position: Vector2D,
            scale: Vector2D,
            color: Color,
            number: int,
            mod_api: ModAPI):
        self.mod_api = mod_api
        self.position = Vector2D.zero()
        self.color = color
        self.scale = scale
        self.next: CheckPoint = None
        self.previous: CheckPoint = None
        self.number = number

        # On versions before 1.7.1.1 top left was considered "center"
        self.center = Vector2D(853/2, 480/2) if self.mod_api._exec_hash == 1802620099 else Vector2D.zero()

        if not hasattr(self, "_initialized"):
            self.image_data = self.mod_api.graphics_manager.load_image(
                "mod_graphics/checkpoint.png"
            )
            self.text = self.mod_api.create_world_text(
                str(self.number), 
                Vector2D.zero(), 
                Color(0xFF, 0xFF, 0xFF, "50%"),
                Color(0, 0, 0, "50%"), 
                1, 
                Vector2D(1, 2), 
                FontStyle.FONT_SMALL,
                1
            )
            super().__init__(
                self.mod_api, 
                self.image_data, 
                Vector2D.zero(), 
                scale, 
                Vector3D.zero(), 
                color, 
                True
            )
            Interactive.__init__(self, self.mod_api)
            Rectangle.__init__(self, position, self.get_dimensions, scale)
            CheckPointContainer.add_checkpoint(self)
        self.deactivate()
        self.set_number(number)
        self._initialized = True

        self.__width_half = self.get_dimensions.x * self.scale.x / 2
        self.__height_half = self.get_dimensions.y * self.scale.y / 2
        self.set_pos_offset(self.center)
        self.set_position(position)

    def activate(self):
        self.set_color(GREEN)
        self.active = True

    def deactivate(self):
        self.set_color(RED)
        self.active = False

    def set_number(self, number):
        self.number = number
        self.text.set_text(str(number))

# Overrides  ----------------------------------- 
    def subscribe(self):
        self.mod_api.subscribe_event(self.on_checkpoint_enter, Event.PLAYER_COLLIDE_ENTER)

    def set_position(self, position: Vector2D):
        self.position = position
        self.set_pos(position)
        self.text.set_pos(position - Vector2D(self.__width_half, self.__height_half) + self.center)
        self.rect_set_pos(position.sub(Vector2D(self.__width_half, self.__height_half)))

# Callbacks -----------------------------------
    def on_checkpoint_enter(self, checkpoint_number: int):
        if checkpoint_number == self.number:
            self.activate()

    def on_checkpoint_exit(self, checkpoint_number: int):
        raise NotImplementedError
# ----------------------------------------------------------------------
    @staticmethod
    def connect_checkpoints(*args):
        num_checkpoints = len(args)
        for i in range(num_checkpoints - 1):
            args[i].next = args[i + 1]
            args[i + 1].previous = args[i]
