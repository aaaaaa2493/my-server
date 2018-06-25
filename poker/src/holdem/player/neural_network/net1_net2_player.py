from random import uniform, random
from typing import Tuple
from core.cards.card import Cards
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.option import Option
from learning.data_sets.decision_model.poker_decision_answer import PokerDecisionAnswer


class Net1Net2Player(BaseNeuralNetworkPlayer):
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

        answer: PokerDecisionAnswer = PokerDecisionAnswer(prediction[0])

        raised_money: int = 0
        if answer is PokerDecisionAnswer.Raise:
            raised_money = evaluation * pot if random() > 0.4 else uniform(0.2, 1) * pot

        return answer.as_option(), raised_money
