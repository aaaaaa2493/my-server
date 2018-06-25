from random import random
from typing import Tuple
from core.cards.card import Cards
from core.cards.rank import Rank
from core.cards.suitability import Suitability
from core.blinds.blinds import Blinds
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.option import Option
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from holdem.poker.strength import Strength
from special.debug import Debug


class Net8Player(BaseNeuralNetworkPlayer):
    def _decide(self, *,
                step: Step,
                to_call: int,
                min_raise: int,
                board: Cards,
                pot: int,
                bb: int,
                strength: Strength,
                players_on_table: int,
                players_active: int,
                players_not_moved: int,
                max_playing_stack: int,
                average_stack_on_table: int,
                **_) -> Tuple[Option, int]:
        if players_on_table < 2 or players_on_table > 10:
            raise ValueError('bad players on table:', players_active)

        if players_active < 2 or players_active > 10:
            raise ValueError('bad players active:', players_active)

        if players_active > players_on_table:
            raise ValueError('bad players active:', players_active, 'with players on table:', players_on_table)

        if players_not_moved < 0 or players_not_moved >= players_active:
            raise ValueError('bad players not moved:', players_not_moved, 'with players active:', players_active)

        evaluation = HoldemPoker.probability(self.cards, board)
        outs: float = HoldemPoker.calculate_outs(self.cards, board)[0]
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
            players_on_table == 2,
            players_on_table == 3,
            players_on_table == 4,
            players_on_table == 5,
            players_on_table == 6,
            players_on_table == 7,
            players_on_table == 8,
            players_on_table == 9,
            players_on_table == 10,
            players_active == 2,
            players_active == 3,
            players_active == 4,
            players_active == 5,
            players_active == 6,
            players_active == 7,
            players_active == 8,
            players_active == 9,
            players_active == 10,
            players_not_moved == 0,
            players_not_moved == 1,
            players_not_moved == 2,
            players_not_moved == 3,
            players_not_moved == 4,
            players_not_moved == 5,
            players_not_moved == 6,
            players_not_moved == 7,
            players_not_moved == 8,
            players_not_moved == 9,
            outs / HoldemPoker.MAX_OUTS,
            self.remaining_money() / bb / Blinds.NORMAL_BBS - 1,
            max_playing_stack / bb / Blinds.NORMAL_BBS - 1,
            average_stack_on_table / bb / Blinds.NORMAL_BBS - 1,
        ))

        Debug.decision("NEURAL NETWORK 8 START THINK")
        Debug.decision('evaluation =', evaluation)
        Debug.decision('pot =', pot)
        Debug.decision('money =', self.money)
        Debug.decision('to_call =', to_call)
        Debug.decision('bb =', bb)
        Debug.decision('step =', step)
        Debug.decision('strength =', strength)
        Debug.decision('first =', first)
        Debug.decision('second =', second)
        Debug.decision('suited =', self.cards.suitability)
        Debug.decision('players_on_table =', players_on_table)
        Debug.decision('players_active =', players_active)
        Debug.decision('players_not_moved =', players_not_moved)
        Debug.decision('outs =', outs)

        answer: PokerDecisionAnswer3 = PokerDecisionAnswer3(prediction[0])

        Debug.decision('ANSWER =', answer)
        Debug.decision("NEURAL NETWORK 8 END THINK")

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
