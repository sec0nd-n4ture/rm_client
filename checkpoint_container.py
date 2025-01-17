from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from checkpoint import CheckPoint

class CheckPointContainer:
    """
    Book keeps the checkpoint objects to avoid unnecessary creation.
    """
    checkpoints: dict[int, CheckPoint] = {}


    @staticmethod
    def add_checkpoint(checkpoint: CheckPoint):
        """
        Called by an uninitialized CheckPoint object
        """
        if checkpoint.number not in CheckPointContainer.checkpoints:
            CheckPointContainer.checkpoints[checkpoint.number] = checkpoint

    @staticmethod
    def get_checkpoint(number: int) -> Optional[CheckPoint]:
        """
        Called by __new__ of a CheckPoint object

        Returns a CheckPoint object that matches with its number attribute.
        
        Returns None when there's no match 
        """
        if number in CheckPointContainer.checkpoints:
            return CheckPointContainer.checkpoints[number]
        return None
