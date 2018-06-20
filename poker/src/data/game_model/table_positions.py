from enum import Enum
from data.game_model.table_position import TablePosition


class TablePositions(Enum):
    Handed10 = TablePosition(3, 3, 2, 2)
    Handed9 = TablePosition(2, 3, 2, 2)
    Handed8 = TablePosition(2, 2, 2, 2)
    Handed7 = TablePosition(1, 2, 2, 2)
    Handed6 = TablePosition(1, 1, 2, 2)
    Handed5 = TablePosition(0, 1, 2, 2)
    Handed4 = TablePosition(0, 0, 2, 2)
    Handed3 = TablePosition(0, 0, 1, 2)
    Handed2 = TablePosition(0, 0, 0, 2)

    @classmethod
    def get_position(cls, players_count: int) -> TablePosition:
        if players_count == 2:
            return TablePositions.Handed2.value
        elif players_count == 3:
            return TablePositions.Handed3.value
        elif players_count == 4:
            return TablePositions.Handed4.value
        elif players_count == 5:
            return TablePositions.Handed5.value
        elif players_count == 6:
            return TablePositions.Handed6.value
        elif players_count == 7:
            return TablePositions.Handed7.value
        elif players_count == 8:
            return TablePositions.Handed8.value
        elif players_count == 9:
            return TablePositions.Handed9.value
        elif players_count == 10:
            return TablePositions.Handed10.value
        else:
            raise ValueError('Bad players count', players_count)
