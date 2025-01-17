SERVER_MAX_PLAYER_SLOTS = 20
SOLDAT_MAX_PLAYER_SLOTS = 32

class BotContainer:
    usable_ids: dict[int, bool] = {x: False for x in range(SERVER_MAX_PLAYER_SLOTS + 1, SOLDAT_MAX_PLAYER_SLOTS - 1)}

    class InsufficentPlayerSlotsError(Exception):
        def __init__(self) -> None:
            return super().__init__(f"Can't instantiate anymore bots, all player slots are in use.")

    @staticmethod
    def mark_id(id: int):
        BotContainer.usable_ids[id] = True

    @staticmethod
    def unmark_id(id: int):
        BotContainer.usable_ids[id] = False

    @staticmethod
    def get_free_id() -> int:
        for id in BotContainer.usable_ids:
            if not BotContainer.usable_ids[id]:
                BotContainer.mark_id(id)
                return id
        raise BotContainer.InsufficentPlayerSlotsError()
