from holdem.play.option import Option
from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer


class PokerDecisionAnswer3(BasePokerDecisionAnswer):
    Fold = 0
    CheckCall = 1
    RaiseSmall = 2
    RaiseMedium = 3
    RaiseALot = 4
    AllIn = 5

    def as_option(self) -> Option:
        if self is PokerDecisionAnswer3.Fold:
            return Option.Fold
        elif self is PokerDecisionAnswer3.CheckCall:
            return Option.CheckCall
        else:
            return Option.Raise
