from random import random, choice
from typing import List
from statistics import mean
from core.cards.card import Cards
from core.cards.rank import Rank
from core.cards.suitability import Suitability
from core.blinds.blinds import Blinds
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.result import Result
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from holdem.poker.strength import Strength
from data.game_model.poker_position import PokerPosition
from special.debug import Debug


class Net11Player(BaseNeuralNetworkPlayer):
    def decide(self, *,
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
               folds_stats: List[float],
               calls_stats: List[float],
               checks_stats: List[float],
               raises_stats: List[float],
               **_) -> Result:

        if random() < 0.1 and 0:
            res = choice([Result.Call, Result.Allin, Result.Raise, Result.Check, Result.Fold])
            if res == Result.Check or res == Result.Fold:
                return res
            if res == Result.Call:
                if self.remaining_money() > to_call:
                    self.pay(to_call)
                    return res
                else:
                    self.go_all_in()
                    return Result.Call
            if res == Result.Allin:
                self.go_all_in()
                return res
            if res == Result.Raise:
                if self.remaining_money() > to_call:

                    ans = random()

                    if ans < 0.25:
                        raised_money = self.remaining_money()
                    elif ans < 0.50:
                        raised_money = (0.25 * random()) * pot
                    elif ans < 0.75:
                        raised_money = (0.25 + 0.5 * random()) * pot
                    else:
                        raised_money = (0.75 + 0.5 * random()) * pot

                    raised_money = int(raised_money)

                    if raised_money < min_raise:
                        raised_money = min_raise

                    if raised_money > self.remaining_money():
                        raised_money = self.remaining_money()

                    if raised_money == self.remaining_money():
                        self.go_all_in()
                        return Result.Allin

                    self.pay(raised_money)
                    return Result.Raise

                else:
                    self.go_all_in()
                    return Result.Call

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

        flop1 = flop2 = flop3 = turn = river = None
        flop_3_suited: int = 0
        flop_2_suited: int = 0
        flop_rainbow: int = 0
        turn_4_suited: int = 0
        turn_3_suited: int = 0
        turn_2_suited_2_not: int = 0
        turn_2_suited_and_other_2: int = 0
        turn_rainbow: int = 0
        river_5_suited: int = 0
        river_4_suited: int = 0
        river_3_suited_2_not: int = 0
        river_3_suited_and_other_2: int = 0
        river_2_suited_and_2_suited: int = 0
        river_only_2_suited: int = 0

        if step.value >= Step.Flop.value:
            cards_sorted = sorted(board[0:3], reverse=True)
            flop1 = cards_sorted[0].rank
            flop2 = cards_sorted[1].rank
            flop3 = cards_sorted[2].rank

            suits = sorted(cards_sorted, key=lambda card: card.suit.value)

            if suits[0].suit == suits[1].suit == suits[2].suit:
                flop_3_suited = 1
            elif suits[0].suit == suits[1].suit or suits[1].suit == suits[2].suit:
                flop_2_suited = 1
            elif suits[0].suit != suits[1].suit != suits[2].suit != suits[0].suit:
                flop_rainbow = 1
            else:
                raise ValueError(f'bad sorted suits {suits}')

        if step.value >= Step.Turn.value:
            turn = board[3].rank

            suits = sorted(board[0:4], key=lambda card: card.suit.value)

            if suits[0].suit == suits[1].suit == suits[2].suit == suits[3].suit:
                turn_4_suited = 1
            elif suits[0].suit == suits[1].suit == suits[2].suit:
                turn_3_suited = 1
            elif suits[1].suit == suits[2].suit == suits[3].suit:
                turn_3_suited = 1
            elif suits[0].suit == suits[1].suit and suits[2].suit == suits[3].suit:
                turn_2_suited_and_other_2 = 1
            elif suits[0].suit == suits[1].suit and suits[2].suit != suits[3].suit:
                turn_2_suited_2_not = 1
            elif suits[1].suit == suits[2].suit and suits[0].suit != suits[3].suit:
                turn_2_suited_2_not = 1
            elif suits[2].suit == suits[3].suit and suits[0].suit != suits[1].suit:
                turn_2_suited_2_not = 1
            elif len(set([suit.suit.value for suit in suits])) == 4:
                turn_rainbow = 1
            else:
                raise ValueError(f'bad suits {suits}')

        if step == Step.River:
            river = board[4].rank

            suits = sorted(board, key=lambda card: card.suit.value)
            diff_suits = len(set([suit.suit.value for suit in suits]))

            if diff_suits == 1:
                river_5_suited = 1
            elif diff_suits == 2 and suits[0].suit == suits[1].suit == suits[2].suit == suits[3].suit:
                river_4_suited = 1
            elif diff_suits == 2 and suits[1].suit == suits[2].suit == suits[3].suit == suits[4].suit:
                river_4_suited = 1
            elif diff_suits == 2 and suits[0].suit == suits[1].suit == suits[2].suit and suits[3].suit == suits[4].suit:
                river_3_suited_and_other_2 = 1
            elif diff_suits == 2 and suits[2].suit == suits[3].suit == suits[4].suit and suits[0].suit == suits[1].suit:
                river_3_suited_and_other_2 = 1
            elif diff_suits == 3 and suits[0].suit == suits[1].suit == suits[2].suit and suits[3].suit != suits[4].suit:
                river_3_suited_2_not = 1
            elif diff_suits == 3 and suits[1].suit == suits[2].suit == suits[3].suit and suits[0].suit != suits[4].suit:
                river_3_suited_2_not = 1
            elif diff_suits == 3 and suits[2].suit == suits[3].suit == suits[4].suit and suits[0].suit != suits[1].suit:
                river_3_suited_2_not = 1
            elif diff_suits == 3 and suits[0].suit == suits[1].suit and suits[2].suit == suits[3].suit:
                river_2_suited_and_2_suited = 1
            elif diff_suits == 3 and suits[0].suit == suits[1].suit and suits[3].suit == suits[4].suit:
                river_2_suited_and_2_suited = 1
            elif diff_suits == 3 and suits[1].suit == suits[2].suit and suits[3].suit == suits[4].suit:
                river_2_suited_and_2_suited = 1
            elif diff_suits == 4:
                river_only_2_suited = 1
            else:
                raise ValueError(f'bad suits {diff_suits} {suits}')

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
            max(raises_stats),
            min(raises_stats),
            mean(raises_stats),
            max(calls_stats),
            min(calls_stats),
            mean(calls_stats),
            max(folds_stats),
            min(folds_stats),
            mean(folds_stats),
            max(checks_stats),
            min(checks_stats),
            mean(checks_stats),
            self.position is PokerPosition.Early,
            self.position is PokerPosition.Middle,
            self.position is PokerPosition.Late,
            self.position is PokerPosition.Blinds,
            flop1 is Rank.Two,
            flop1 is Rank.Three,
            flop1 is Rank.Four,
            flop1 is Rank.Five,
            flop1 is Rank.Six,
            flop1 is Rank.Seven,
            flop1 is Rank.Eight,
            flop1 is Rank.Nine,
            flop1 is Rank.Ten,
            flop1 is Rank.Jack,
            flop1 is Rank.Queen,
            flop1 is Rank.King,
            flop1 is Rank.Ace,
            flop2 is Rank.Two,
            flop2 is Rank.Three,
            flop2 is Rank.Four,
            flop2 is Rank.Five,
            flop2 is Rank.Six,
            flop2 is Rank.Seven,
            flop2 is Rank.Eight,
            flop2 is Rank.Nine,
            flop2 is Rank.Ten,
            flop2 is Rank.Jack,
            flop2 is Rank.Queen,
            flop2 is Rank.King,
            flop2 is Rank.Ace,
            flop3 is Rank.Two,
            flop3 is Rank.Three,
            flop3 is Rank.Four,
            flop3 is Rank.Five,
            flop3 is Rank.Six,
            flop3 is Rank.Seven,
            flop3 is Rank.Eight,
            flop3 is Rank.Nine,
            flop3 is Rank.Ten,
            flop3 is Rank.Jack,
            flop3 is Rank.Queen,
            flop3 is Rank.King,
            flop3 is Rank.Ace,
            turn is Rank.Two,
            turn is Rank.Three,
            turn is Rank.Four,
            turn is Rank.Five,
            turn is Rank.Six,
            turn is Rank.Seven,
            turn is Rank.Eight,
            turn is Rank.Nine,
            turn is Rank.Ten,
            turn is Rank.Jack,
            turn is Rank.Queen,
            turn is Rank.King,
            turn is Rank.Ace,
            river is Rank.Two,
            river is Rank.Three,
            river is Rank.Four,
            river is Rank.Five,
            river is Rank.Six,
            river is Rank.Seven,
            river is Rank.Eight,
            river is Rank.Nine,
            river is Rank.Ten,
            river is Rank.Jack,
            river is Rank.Queen,
            river is Rank.King,
            river is Rank.Ace,
            flop_3_suited,
            flop_2_suited,
            flop_rainbow,
            turn_4_suited,
            turn_3_suited,
            turn_2_suited_2_not,
            turn_2_suited_and_other_2,
            turn_rainbow,
            river_5_suited,
            river_4_suited,
            river_3_suited_2_not,
            river_3_suited_and_other_2,
            river_2_suited_and_2_suited,
            river_only_2_suited,
        ))

        Debug.decision("NEURAL NETWORK 10 START THINK")
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
        Debug.decision("NEURAL NETWORK 10 END THINK")

        if answer is PokerDecisionAnswer3.Fold:
            self.fold()
            return Result.Fold

        elif answer is PokerDecisionAnswer3.CheckCall:
            if self.remaining_money() > to_call:
                if to_call == 0 or self.gived == to_call:
                    return Result.Check
                else:
                    self.pay(to_call)
                    return Result.Call
            else:
                self.go_all_in()
                return Result.Call

        else:
            if self.remaining_money() > to_call:

                if answer == PokerDecisionAnswer3.AllIn:
                    raised_money = self.remaining_money()
                elif answer == PokerDecisionAnswer3.RaiseSmall:
                    raised_money = (0.25 * random()) * pot
                elif answer == PokerDecisionAnswer3.RaiseMedium:
                    raised_money = (0.25 + 0.5 * random()) * pot
                else:
                    raised_money = (0.75 + 0.5 * random()) * pot

                raised_money = int(raised_money)

                if raised_money < min_raise:
                    raised_money = min_raise

                if raised_money > self.remaining_money():
                    raised_money = self.remaining_money()

                if raised_money == self.remaining_money():
                    self.go_all_in()
                    return Result.Allin

                self.pay(raised_money)
                return Result.Raise

            else:
                self.go_all_in()
                return Result.Call
