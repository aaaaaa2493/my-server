from core.cards.card import Card
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.result import Result
from learning.data_sets.decision_model.poker_decision_answer_2 import PokerDecisionAnswer2


class Net3Player(BaseNeuralNetworkPlayer):
    def decide(self, step: Step, to_call: int, min_raise: int, board: Card.Cards, pot: int, bb: int) -> Result:

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

        if answer is PokerDecisionAnswer2.Fold:
            self.fold()
            return Result.Fold

        elif answer is PokerDecisionAnswer2.CheckCall:
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

                if answer == PokerDecisionAnswer2.AllIn:
                    raised_money = self.remaining_money()
                elif answer == PokerDecisionAnswer2.Raise_10:
                    raised_money = pot * 0.10
                elif answer == PokerDecisionAnswer2.Raise_25:
                    raised_money = pot * 0.25
                elif answer == PokerDecisionAnswer2.Raise_40:
                    raised_money = pot * 0.40
                elif answer == PokerDecisionAnswer2.Raise_55:
                    raised_money = pot * 0.55
                elif answer == PokerDecisionAnswer2.Raise_70:
                    raised_money = pot * 0.70
                elif answer == PokerDecisionAnswer2.Raise_85:
                    raised_money = pot * 0.85
                else:
                    raised_money = pot

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
