from random import random
from core.cards.card import Card
from holdem.player.neural_network.base_neural_network_player import BaseNeuralNetworkPlayer
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from holdem.play.result import Result
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from holdem.poker.strength import Strength


class Net5Player(BaseNeuralNetworkPlayer):
    def decide(self,
               step: Step,
               to_call: int,
               min_raise: int,
               board: Card.Cards,
               pot: int,
               bb: int,
               strength: Strength
               ) -> Result:

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
