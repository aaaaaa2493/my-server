from holdem.play.option import Option
from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer


class PokerDecisionAnswer(BasePokerDecisionAnswer):
    Fold = 0
    CheckCall = 1
    Raise = 2

    def as_option(self) -> Option:
        if self is PokerDecisionAnswer.Fold:
            return Option.Fold
        elif self is PokerDecisionAnswer.CheckCall:
            return Option.CheckCall
        else:
            return Option.Raise
