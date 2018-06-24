from random import random
from typing import Tuple
from core.cards.card import Cards
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.option import Option
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from holdem.poker.strength import Strength


class Net5Player(BaseNeuralNetworkPlayer):
    def _decide(self, *,
                step: Step,
                to_call: int,
                min_raise: int,
                board: Cards,
                pot: int,
                bb: int,
                strength: Strength,
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
            step is Step.River,
            strength is Strength.RoyalFlush,
            strength is Strength.StraightFlush,
            strength is Strength.Quad,
            strength is Strength.FullHouse,
            strength is Strength.Flush,
            strength is Strength.Straight,
            strength is Strength.Set,
            strength is Strength.Pairs,
            strength is Strength.Pair,
            strength is Strength.Nothing
        ))

        answer: PokerDecisionAnswer3 = PokerDecisionAnswer3(prediction[0])
        raise_amount = 0
        if answer is PokerDecisionAnswer3.AllIn:
            raise_amount = self.remaining_money()
        elif answer is PokerDecisionAnswer3.RaiseSmall:
            raise_amount = (0.1 + 0.25 * random()) * pot
        elif answer is PokerDecisionAnswer3.RaiseMedium:
            raise_amount = (0.25 + 0.4 * random()) * pot
        elif answer is PokerDecisionAnswer3.RaiseALot:
            raise_amount = (0.6 + 0.6 * random()) * pot

        return answer.as_option(), raise_amount
