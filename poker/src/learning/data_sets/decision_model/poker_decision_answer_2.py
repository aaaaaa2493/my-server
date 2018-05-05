from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer


class PokerDecisionAnswer2(BasePokerDecisionAnswer):
    Fold = 0
    CheckCall = 1
    Raise_10 = 2
    Raise_25 = 3
    Raise_40 = 4
    Raise_55 = 5
    Raise_70 = 6
    Raise_85 = 7
    Raise_100 = 8
    AllIn = 9
