from typing import List, Callable, Tuple
from operator import add, sub, mul, truediv, neg, gt
from random import random, choice


class Neural:

    class Node:

        def __init__(self, value: float = 0, relation: 'Neural.Relation' = None):
            self.value: float = value
            self.relation = relation

        def __call__(self) -> float:
            if self.relation is None:
                return self.value
            else:
                return self.relation()

        def __getitem__(self, item) -> None:
            self.value = item

    Nodes = List[Node]

    OperationType = int
    Binary = 2
    Unary = 1

    Operation = Callable[..., float]
    Operations: List[Tuple[Operation, OperationType]] = [(add, Binary), (sub, Binary),
                                                         (truediv, Binary), (mul, Binary),
                                                         (pow, Binary), (gt, Binary),
                                                         (neg, Unary), (abs, Unary)]

    class Relation:

        def __init__(self, op: 'Neural.Operation', n1: 'Neural.Node', n2: 'Neural.Node' = None):
            self.first: Neural.Node = n1
            self.second: Neural.Node = n2
            self.op: Neural.Operation = op

            self.result: Neural.Node = Neural.Node(self(), self)

        def __call__(self) -> float:
            try:
                if self.second is None:
                    return self.op(self.first())
                else:
                    return self.op(self.first(), self.second())

            except ZeroDivisionError:
                return 0

    def __init__(self):

        # Result Node, stores how much can bet to this hand to this opponent coefficients
        self.result = None

        # Need constant because most coefficients are probabilities from 0 to 1
        self.const_1 = Neural.Node(1)

        # From BasePlay, divided by total
        self.fold = Neural.Node()
        self.check = Neural.Node()
        self.bet = Neural.Node()
        self.raise_ = Neural.Node()
        self.bet3 = Neural.Node()
        self.bet4 = Neural.Node()
        self.allin = Neural.Node()
        self.call_r = Neural.Node()
        self.call_3 = Neural.Node()
        self.call_4 = Neural.Node()
        self.call_a = Neural.Node()
        self.check_fold = Neural.Node()
        self.bet_fold = Neural.Node()
        self.call_fold = Neural.Node()
        self.raise_fold = Neural.Node()
        self.check_call = Neural.Node()
        self.check_raise = Neural.Node()
        self.check_allin = Neural.Node()
        self.wins = Neural.Node()

        # From Play, divided by total hands
        self.wins_before_showdown = Neural.Node()
        self.wins_after_showdown = Neural.Node()
        self.goes_to_showdown = Neural.Node()

        # More far from small blinds - the number is bigger
        self.my_position = Neural.Node()
        self.his_position = Neural.Node()

        # remaining_money()
        self.my_stack = Neural.Node()
        self.his_stack = Neural.Node()

        # .gived
        self.his_decision = Neural.Node()
        self.me_already_gived = Neural.Node()

        # .in_pot + .gived
        self.in_pot = Neural.Node()

        # Probability from Poker.probability
        self.probability = Neural.Node()
        self.outs = Neural.Node()

        # Blinds situation
        self.small_blind = Neural.Node()
        self.big_blind = Neural.Node()
        self.ante = Neural.Node()

        # 1 if action is on this stage else 0
        self.is_preflop = Neural.Node()
        self.is_flop = Neural.Node()
        self.is_turn = Neural.Node()
        self.is_river = Neural.Node()

        self.base: Neural.Nodes = [self.const_1, self.fold, self.check, self.bet, self.raise_, self.bet3, self.bet4,
                                   self.allin, self.call_r, self.call_3, self.call_4, self.call_a,
                                   self.check_fold, self.bet_fold, self.call_fold, self.raise_fold,
                                   self.check_call, self.check_raise, self.check_allin, self.wins,
                                   self.wins_before_showdown, self.wins_after_showdown, self.goes_to_showdown,
                                   self.my_position, self.his_position, self.my_stack, self.his_stack,
                                   self.his_decision, self.me_already_gived, self.in_pot,
                                   self.probability, self.outs, self.small_blind, self.big_blind, self.ante,
                                   self.is_preflop, self.is_flop, self.is_turn, self.is_river]

        self.secondary: Neural.Nodes = []
        self.mutate()

    def mutate(self):

        for _ in range(10):

            if random() < 0.5:

                relation, params = choice(Neural.Operations)

                if params == Neural.Binary:

                    first_node = choice(self.base + self.secondary)
                    second_node = choice(self.base + self.secondary)
                    self.secondary += [Neural.Relation(relation, first_node, second_node).result]

                elif params == Neural.Unary:

                    node = choice(self.base + self.secondary)
                    self.secondary += [Neural.Relation(relation, node).result]

        self.result = choice(self.base + self.secondary)
