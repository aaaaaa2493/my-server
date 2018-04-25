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
