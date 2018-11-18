from __future__ import annotations
from numpy import array
from typing import List, Dict
from holdem.poker.holdem_poker import HoldemPoker
from holdem.play.step import Step
from data.game_model.event import Event
from data.game_model.poker_hand import PokerHand
from data.game_model.poker_game import PokerGame
from learning.data_sets.decision_model.base_poker_decision import BasePokerDecision
from learning.data_sets.decision_model.base_poker_decision_answer import BasePokerDecisionAnswer
from learning.data_sets.decision_model.poker_decision_answer_3 import PokerDecisionAnswer3
from special.debug import Debug


class PokerDecision3(BasePokerDecision):
    def __init__(self):
        super().__init__()
        self.probability_to_win: float = 0
        self.my_money: int = 0
        self.money_in_pot: int = 0
        self.money_to_call: int = 0
        self.big_blind: int = 0
        self.is_preflop: int = 0
        self.is_flop: int = 0
        self.is_turn: int = 0
        self.is_river: int = 0

    def to_array(self) -> array:
        arr = [
            self.probability_to_win,
            self.my_money / self.money_in_pot,
            self.money_to_call / self.money_in_pot,
            self.big_blind / self.money_in_pot,
            self.is_preflop,
            self.is_flop,
            self.is_turn,
            self.is_river,
        ]
        return array(arr)

    def __str__(self) -> str:
        return f'{self._answer.name} ' \
               f'money {self.my_money} ' \
               f'pot {self.money_in_pot} ' \
               f'bb {self.big_blind} ' \
               f'call {self.money_to_call} ' \
               f'prob {self.probability_to_win} '

    @staticmethod
    def create(res: BasePokerDecisionAnswer, prob: float,
               money: int, pot: int, call: int, bb: int, step: Step) -> PokerDecision3:
        if prob < 0 or prob > 1:
            raise ValueError(f'Probability must be in [0, 1], gived {prob}')

        if money < 0:
            raise ValueError(f'Money must be > 0, gived {money}')

        if pot < 0:
            raise ValueError(f'Pot must be > 0, gived {pot}')

        if call < 0:
            raise ValueError(f'Call must be > 0, gived {call}')

        if bb < 0:
            raise ValueError(f'Big blinds must be > 0, gived {bb}')

        if pot <= call and step != Step.Preflop:
            raise ValueError(f'Pot must be > call, gived call {call} pot {pot}')

        if type(res) is not PokerDecisionAnswer3:
            raise ValueError(f'Result must ne instance of PokerDecisionAnswer, gived {res}')

        des = PokerDecision3()
        des.set_answer(res)
        des.probability_to_win = prob
        des.my_money = money
        des.money_in_pot = pot
        des.money_to_call = call
        des.big_blind = bb

        if step == Step.Preflop:
            des.is_preflop = 1
        elif step == Step.Flop:
            des.is_flop = 1
        elif step == Step.Turn:
            des.is_turn = 1
        elif step == Step.River:
            des.is_river = 1

        return des

    @staticmethod
    def get_decisions(game: PokerGame, hand: PokerHand) -> List[BasePokerDecision]:

        decisions: List[BasePokerDecision] = []

        pot_size = 0

        money: Dict[str, int] = {p.name: p.money for p in hand.players}
        bb: int = hand.big_blind

        Debug.datasets(')' * 20)
        for n, v in money.items():
            Debug.datasets(f'{n} - {v}')
        Debug.datasets('(' * 20)

        for step, stage in hand:
            Debug.datasets('NEW STEP', step)
            gived: Dict[str, int] = {p.name: 0 for p in hand.players}

            if step == Step.Preflop:
                raise_amount = hand.big_blind
            else:
                raise_amount = 0

            for act in stage:
                if act.event.is_statement():
                    continue

                Debug.datasets(act, raise_amount)

                if act.event == Event.Ante:
                    pot_size += act.money
                    money[act.player.name] -= act.money

                elif act.event == Event.SmallBlind:
                    pot_size += act.money
                    gived[act.player.name] = act.money
                    money[act.player.name] -= act.money

                elif act.event == Event.BigBlind:
                    pot_size += act.money
                    gived[act.player.name] = act.money
                    money[act.player.name] -= act.money

                elif act.event == Event.Fold:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        pr = HoldemPoker.probability(act.player.cards, hand.board.get_from_step(step))
                        my_money = money[act.player.name]
                        to_call = raise_amount - gived[act.player.name]
                        des = PokerDecision3.create(PokerDecisionAnswer3.Fold, pr,
                                                    my_money, pot_size, to_call, bb, step)
                        decisions += [des]

                elif act.event == Event.Check:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        pr = HoldemPoker.probability(act.player.cards, hand.board.get_from_step(step))
                        my_money = money[act.player.name]
                        to_call = raise_amount - gived[act.player.name]
                        des = PokerDecision3.create(PokerDecisionAnswer3.CheckCall, pr,
                                                    my_money, pot_size, to_call, bb, step)
                        decisions += [des]

                elif act.event == Event.Call:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        pr = HoldemPoker.probability(act.player.cards, hand.board.get_from_step(step))
                        my_money = money[act.player.name]
                        if raise_amount > my_money + gived[act.player.name]:
                            to_call = my_money
                        else:
                            to_call = raise_amount - gived[act.player.name]
                        des = PokerDecision3.create(PokerDecisionAnswer3.CheckCall, pr,
                                                    my_money, pot_size, to_call, bb, step)
                        decisions += [des]
                    pot_size += act.money - gived[act.player.name]
                    money[act.player.name] -= act.money - gived[act.player.name]
                    gived[act.player.name] = act.money

                elif act.event == Event.Raise or act.event == Event.Allin:
                    if act.player.cards is not None and act.player.cards.initialized() and not act.player.is_loser:
                        pr = HoldemPoker.probability(act.player.cards, hand.board.get_from_step(step))
                        my_money = money[act.player.name]
                        to_call = raise_amount - gived[act.player.name]

                        actually_raised = act.money - gived[act.player.name]
                        pot_sized_raise = actually_raised / pot_size
                        if my_money == actually_raised:
                            answer = PokerDecisionAnswer3.AllIn
                        elif pot_sized_raise < 0.25:
                            answer = PokerDecisionAnswer3.RaiseSmall
                        elif pot_sized_raise < 0.75:
                            answer = PokerDecisionAnswer3.RaiseMedium
                        else:
                            answer = PokerDecisionAnswer3.RaiseALot

                        des = PokerDecision3.create(answer, pr, my_money, pot_size, to_call, bb, step)
                        decisions += [des]
                    pot_size += act.money - gived[act.player.name]
                    money[act.player.name] -= act.money - gived[act.player.name]
                    gived[act.player.name] = act.money
                    if raise_amount < act.money:
                        raise_amount = act.money

                elif act.event == Event.ReturnMoney:
                    pot_size -= act.money

                else:
                    raise ValueError('you forget about', act.event)

                Debug.datasets(')' * 20)
                for n, v in gived.items():
                    Debug.datasets(f'{n}: {money[n]} ({v})')
                Debug.datasets('(' * 20)

        Debug.datasets('*' * 20)

        for des in decisions:
            Debug.datasets(des)

        Debug.datasets('_' * 20)
        return decisions
