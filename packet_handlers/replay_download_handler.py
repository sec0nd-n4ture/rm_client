from db_shared_utils.db_shared import ReplayData
from db_client.handler import *
import json

class ReplayDownloadHandler(BaseHandler):
    def __init__(self, packet: BasePacket, client_socket: socket.socket) -> None:
        super().__init__(packet, client_socket)

    def handle(self):
        snap_count = int.from_bytes(self.packet.data[:4], "little")
        replay_data: ReplayData = ReplayData()
        replay_length = snap_count * ReplayData.snapshot_size
        if snap_count != 0:
            replay_length = snap_count * ReplayData.snapshot_size
            replay_data.set_data(self.packet.data[4:replay_length])
        response = json.loads(self.packet.data[replay_length+4:])

        replay_id = response["replay_id"]
        self.notify_sub_handlers(replay_id, snap_count, ReplayData.copy(replay_data))
