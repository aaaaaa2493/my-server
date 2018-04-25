from typing import Dict
from special.ordered_enum import OrderedEnum


class LastGameStep(Exception):
    pass


class Step(OrderedEnum):
    Preflop = 1
    Flop = 2
    Turn = 3
    River = 4

    @classmethod
    def next_step(cls, step: 'Step') -> 'Step':

        if step == Step.Preflop:
            return Step.Flop
        elif step == Step.Flop:
            return Step.Turn
        elif step == Step.Turn:
            return Step.River

        raise LastGameStep(f'No next step id for {step}')

    def __str__(self) -> str:
        return _to_str[self]


_to_str: Dict[Step, str] = {
    Step.Preflop: 'preflop',
    Step.Flop: 'flop',
    Step.Turn: 'turn',
    Step.River: 'river'
}
