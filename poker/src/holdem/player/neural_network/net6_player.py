from random import random
from typing import Tuple
from core.cards.card import Cards
from core.cards.rank import Rank
from core.cards.suitability import Suitability
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.option import Option
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from holdem.poker.strength import Strength


class Net6Player(BaseNeuralNetworkPlayer):
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
        first: Rank = self.cards.first.rank
        second: Rank = self.cards.second.rank
        prediction = self.nn.predict(self.create_input(
            evaluation,
            self.money / pot,
            to_call / pot,
            bb / pot,
            step is Step.Preflop,
            step is Step.Flop,
            step is Step.Turn,
            step is Step.River,
            strength is Strength.Nothing,
            strength is Strength.Pair,
            strength is Strength.Pairs,
            strength is Strength.Set,
            strength is Strength.Straight,
            strength is Strength.Flush,
            strength is Strength.FullHouse,
            strength is Strength.Quad,
            strength is Strength.StraightFlush,
            strength is Strength.RoyalFlush,
            first is Rank.Two,
            first is Rank.Three,
            first is Rank.Four,
            first is Rank.Five,
            first is Rank.Six,
            first is Rank.Seven,
            first is Rank.Eight,
            first is Rank.Nine,
            first is Rank.Ten,
            first is Rank.Jack,
            first is Rank.Queen,
            first is Rank.King,
            first is Rank.Ace,
            second is Rank.Two,
            second is Rank.Three,
            second is Rank.Four,
            second is Rank.Five,
            second is Rank.Six,
            second is Rank.Seven,
            second is Rank.Eight,
            second is Rank.Nine,
            second is Rank.Ten,
            second is Rank.Jack,
            second is Rank.Queen,
            second is Rank.King,
            second is Rank.Ace,
            self.cards.suitability is Suitability.Suited,
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
