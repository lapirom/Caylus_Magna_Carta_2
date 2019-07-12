from enum import Enum, unique

@unique
class Location(Enum):
    """Enumeration of all the possible locations of the player buildings."""
    HAND = 0
    PILE = 1
    DISCARD = 2
    ROAD = 3
    REPLACED = 4