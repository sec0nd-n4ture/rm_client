from soldat_extmod_api.player_helper.player import Player
from soldat_extmod_api.mod_api import ModAPI, MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE

class RmPlayer(Player):
    def __init__(self, mod_api, id: int):
        super().__init__(mod_api, id)
        self.mod_api: ModAPI = mod_api

        respawn_code = f'''
        mov eax, {hex(self.tsprite_object_addr)}
        call TSprite.Respawn
        xor eax, eax
        call RtlExitUserThread
        '''

        self.respawn_code_addr = self.mod_api.soldat_bridge.allocate_memory(
            256, 
            MEM_COMMIT | MEM_RESERVE, 
            PAGE_EXECUTE_READWRITE
        )
        assembled_code = self.mod_api.assembler.assemble(respawn_code, self.respawn_code_addr)
        self.mod_api.soldat_bridge.write(self.respawn_code_addr, assembled_code)

    def respawn(self):
        self.mod_api.soldat_bridge.execute(self.respawn_code_addr, None, False, free_after_use=False)

    def take_movement_snapshot(self):
        wmpos = self.get_mouse_world_pos().to_bytes()
        pos = self.get_position_bytes()
        vel = self.get_velocity().to_bytes()
        fk = self.get_first_keystates()
        sk = self.get_second_keystates()
        snapshot = wmpos + pos + vel + fk + sk
        return snapshot
