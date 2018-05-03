from pickle import load
from random import uniform, random
from numpy import array
from sklearn.neural_network import MLPClassifier
from core.cards.card import Card
from holdem.poker.holdem_poker import HoldemPoker
from holdem.player.player import Player
from holdem.play.play import Play
from holdem.play.step import Step
from holdem.play.result import Result
from holdem.base_network import BaseNetwork
from learning.data_sets.decision_model.poker_decision_answer import PokerDecisionAnswer


class NeuralNetworkPlayer(Player):
    def __init__(self, _id: int, money: int, path: str):
        super().__init__(_id, money, False, path, Play(), BaseNetwork())
        self.nn: MLPClassifier = load(open(f'networks/{path}', 'rb'))

    @staticmethod
    def create_input(*args):
        return array([array(args)])

    def decide(self, step: Step, to_call: int, min_raise: int, cards: Card.Cards, pot: int, bb: int):

        if not self.in_game:
            return Result.DoNotPlay

        if self.money == 0 and self.in_game:
            return Result.InAllin

        evaluation = HoldemPoker.probability(self.cards, cards)
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

        if answer is PokerDecisionAnswer.Fold:
            self.fold()
            return Result.Fold

        elif answer is PokerDecisionAnswer.CheckCall:
            if self.remaining_money() > to_call:
                if to_call == 0 or self.gived == to_call:
                    return Result.Check
                else:
                    self.pay(to_call)
                    return Result.Call
            else:
                self.go_all_in()
                return Result.Call

        elif answer is PokerDecisionAnswer.Raise:
            if self.remaining_money() > to_call:

                raised_money = int(evaluation * pot if random() > 0.4 else uniform(0.2, 1) * pot)

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
