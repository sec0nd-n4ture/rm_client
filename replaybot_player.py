from soldat_extmod_api.mod_api import ModAPI, Vector2D, MEM_COMMIT, MEM_RESERVE, PAGE_READWRITE, PAGE_EXECUTE_READWRITE
from soldat_extmod_api.game_structs.player_struct import TPlayer
from soldat_extmod_api.player_helper.player import Player
from db_shared_utils.db_shared import ReplayData
from bot_container import BotContainer



class ReplayBot(Player):
    def __new__(cls):
        try:
            id = BotContainer.get_free_id()
            replaybot = super().__new__(cls)
            replaybot.id = id
            return replaybot
        except BotContainer.InsufficentPlayerSlotsError:
            return None

    def __init__(self):
        self.mod_api = ModAPI() # singleton workaround
        super().__init__(self.mod_api, self.id)
        self.soldat_bridge = self.mod_api.soldat_bridge
        self.snapshot_index = 0
        self.replay_data: ReplayData = None
        self.paused = False

    def add(self, 
        bot_name: str, 
        position: Vector2D = Vector2D.zero(), 
        velocity: Vector2D = Vector2D.zero(), 
        skin_color: int = 0x00000000
    ):
        szName = bot_name.encode("utf-8") + b"\x00"
        nameptr = self.soldat_bridge.allocate_memory(
            len(szName), 
            MEM_COMMIT | MEM_RESERVE, 
            PAGE_READWRITE
        )
        self.soldat_bridge.write(nameptr, szName)

        player = TPlayer()
        player.Port = 0
        player.SkinColor = skin_color
        player.Color1 = skin_color
        player.Color2 = skin_color
        player.State = b"\x2a" # playing
        player.Team = b"\x00"
        player.ControlMethod = b"\x01" # human

        player_bytes = player.to_bytes()
        pos_bytes = position.to_bytes()
        vel_bytes = velocity.to_bytes()

        playerptr = self.soldat_bridge.allocate_memory(
            len(player_bytes), 
            MEM_COMMIT | MEM_RESERVE, 
            PAGE_READWRITE
        )
        self.soldat_bridge.write(playerptr, player_bytes)

        argsptr = self.soldat_bridge.allocate_memory(
            len(pos_bytes)*2, 
            MEM_COMMIT | MEM_RESERVE, 
            PAGE_READWRITE
        )

        self.soldat_bridge.write(argsptr, pos_bytes+vel_bytes)
        arg_sym_table = {
            "player_ptr": playerptr,
            "pos_ptr":    argsptr,
            "name_ptr":   nameptr,
            "vel_ptr":    argsptr + 0x8
        }
        self.mod_api.assembler.add_to_symbol_table(arg_sym_table)

        create_sprite_code = f'''
        sub esp, 0x80
        mov eax, player_ptr
        mov ecx, 18
        mov edx, name_ptr
        call LStrFromArray
        push {hex(self.id)}
        push eax
        mov ecx, 0x01
        mov edx, pos_ptr
        mov eax, vel_ptr
        call CreateSprite
        xor eax, eax
        call RtlExitUserThread
        '''

        code_addr = self.soldat_bridge.allocate_memory(
            512, 
            MEM_COMMIT | MEM_RESERVE, 
            PAGE_EXECUTE_READWRITE
        )

        assembled_code = self.mod_api.assembler.assemble(
            create_sprite_code, 
            code_addr
        )

        self.soldat_bridge.write(code_addr, assembled_code)
        self.soldat_bridge.execute(
            code_addr, 
            None, 
            blocking=False, 
            free_after_use=True
        )

    def update_position(self, new_position):
        self.set_position(new_position)

    def update_velocity(self, new_velocity: Vector2D | bytes):
        self.set_velocity(new_velocity)

    def set_transparency(self, new_transparency: bytes):
        super().set_transparency(new_transparency)

    def update_mouse_pos(self, new_pos: bytes):
        self.set_mouse_world_pos(new_pos)

    def update_first_keystates(self, new_keystates: bytes):
        self.set_first_keystates(new_keystates)

    def update_second_keystates(self, new_keystates: bytes):
        self.set_second_keystates(new_keystates)

    def inject_replay_movement(self):
        if self.replay_data.get_snapshots_len != 0:
            self.update_first_keystates(self.replay_data.get_first_keystates(self.snapshot_index))
            self.update_second_keystates(self.replay_data.get_second_keystates(self.snapshot_index))
            self.update_position(self.replay_data.get_position(self.snapshot_index))
            self.update_first_keystates(self.replay_data.get_first_keystates(self.snapshot_index))
            if self.paused:
                self.update_velocity(Vector2D.zero())
            else:
                self.update_velocity(self.replay_data.get_velocity(self.snapshot_index))
            self.update_mouse_pos(self.replay_data.get_mouse_pos(self.snapshot_index))

    @property
    def replay_max_index(self):
        return self.replay_data.get_snapshots_len

    def pause(self):
        self.paused = True

    def play(self):
        self.paused = False

    def deactivate(self):
        self.set_active(False)

    def free(self):
        BotContainer.unmark_id(self.id)

    def __del__(self):
        self.deactivate()
        self.free()
