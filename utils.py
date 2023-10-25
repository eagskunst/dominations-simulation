from __future__ import annotations  # <-- Additional import.
import typing
if typing.TYPE_CHECKING:
    from models import Nation, Resources, Combat

class EventAdditionError(Exception):
    """
    Custom exception to signal issues when trying to add events.
    
    Attributes:
        message (str): Descriptive message for the error.
    """
    def __init__(self, message) -> None:
        super().__init__(message)

def get_buildings_count(nation: Nation, res: Resources, combat: Combat):
    return nation.houses_count + len(res.gold_food_buildings) + combat.attack_buildings_count