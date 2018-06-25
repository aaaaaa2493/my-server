from typing import Tuple
from core.cards.card import Cards
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.option import Option
from learning.data_sets.decision_model.poker_decision_answer_2 import PokerDecisionAnswer2


class Net3Player(BaseNeuralNetworkPlayer):
    def _decide(self, *,
                step: Step,
                to_call: int,
                min_raise: int,
                board: Cards,
                pot: int,
                bb: int,
                **_) -> Tuple[Option, int]:

        evaluation = HoldemPoker.probability(self.cards, board)
        prediction = self.nn.predict(self.create_input(
            evaluation,
            self.money / pot,
            to_call / pot,
            bb / pot,
            step is Step.Preflop,
            step is Step.Flop,
            step is Step.Turn,
            step is Step.River
        ))

        answer: PokerDecisionAnswer2 = PokerDecisionAnswer2(prediction[0])
        raised_money = 0
        if answer is PokerDecisionAnswer2.AllIn:
            raised_money = self.remaining_money()
        elif answer is PokerDecisionAnswer2.Raise_10:
            raised_money = pot * 0.10
        elif answer is PokerDecisionAnswer2.Raise_25:
            raised_money = pot * 0.25
        elif answer is PokerDecisionAnswer2.Raise_40:
            raised_money = pot * 0.40
        elif answer is PokerDecisionAnswer2.Raise_55:
            raised_money = pot * 0.55
        elif answer is PokerDecisionAnswer2.Raise_70:
            raised_money = pot * 0.70
        elif answer is PokerDecisionAnswer2.Raise_85:
            raised_money = pot * 0.85
        elif answer is PokerDecisionAnswer2.Raise_100:
            raised_money = pot

        return answer.as_option(), raised_money
