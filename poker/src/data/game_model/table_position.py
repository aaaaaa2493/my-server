from enum import Enum


class TablePosition(Enum):
    Handed10 = (3, 3, 2, 2)
    Handed9 = (3, 2, 2, 2)
    Handed8 = (2, 2, 2, 2)
    Handed7 = (2, 1, 2, 2)
    Handed6 = (1, 1, 2, 2)
    Handed5 = (1, 1, 1, 2)
    Handed4 = (1, 0, 1, 2)
    Handed3 = (0, 0, 1, 2)
    Handed2 = (0, 0, 0, 2)
