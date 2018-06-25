from typing import Dict
from special.ordered_enum import OrderedEnum


class LastGameStep(Exception):
    pass


class Step(OrderedEnum):
    Preflop = 1
    Flop = 2
    Turn = 3
    River = 4

    def next_step(self) -> 'Step':

        if self == Step.Preflop:
            return Step.Flop
        elif self == Step.Flop:
            return Step.Turn
        elif self == Step.Turn:
            return Step.River

        raise LastGameStep(f'No next step id for {self}')

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Step, str] = {
    Step.Preflop: 'preflop',
    Step.Flop: 'flop',
    Step.Turn: 'turn',
    Step.River: 'river'
}
