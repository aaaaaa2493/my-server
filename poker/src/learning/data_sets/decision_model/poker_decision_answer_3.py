from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer


class PokerDecisionAnswer3(BasePokerDecisionAnswer):
    Fold = 0
    CheckCall = 1
    RaiseSmall = 2
    RaiseMedium = 3
    RaiseALot = 4
    AllIn = 5
