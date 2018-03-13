from typing import List
from datetime import datetime
from random import random, uniform
from time import sleep
from special.debug import Debug
from holdem.base_play import Decision, Step, Result
from holdem.holdem_poker import HoldemPoker as Poker, Hand
from holdem.cards_pair import CardsPair
from holdem.play_manager import Play, PlayManager
from holdem.base_play import BasePlay
from holdem.network import Network
from core.card import Card


class Player:

    class History:

        Decisions = List[Decision]

        def __init__(self):

            self.preflop: Decision = None
            self.flop: Decision = None
            self.turn: Decision = None
            self.river: Decision = None

        def drop(self) -> None:

            self.preflop: Decision = None
            self.flop: Decision = None
            self.turn: Decision = None
            self.river: Decision = None

        @staticmethod
        def decide(curr: Decision, decision: Decision) -> Decision:

            if curr is None:
                if decision == Decision.Fold:
                    return Decision.CheckFold

                return decision

            else:

                if decision == Decision.Fold and curr == Decision.Check:
                    return Decision.CheckFold

                elif decision == Decision.Fold and (curr == Decision.CheckCall or
                                                    curr == Decision.CallR or
                                                    curr == Decision.Call3 or
                                                    curr == Decision.Call4):
                    return Decision.CallFold

                elif decision == Decision.Fold and curr == Decision.Bet:
                    return Decision.BetFold

                elif decision == Decision.Fold and (curr == Decision.Raise or
                                                    curr == Decision.Bet3 or
                                                    curr == Decision.Bet4 or
                                                    curr == Decision.CheckRaise):
                    return Decision.RaiseFold

                elif curr == Decision.Check and (decision == Decision.CheckCall or
                                                 decision == Decision.CallR or
                                                 decision == Decision.Call3 or
                                                 decision == Decision.Call4 or
                                                 decision == Decision.CallA):
                    return decision

                elif curr == Decision.Check and (decision == Decision.Raise or
                                                 decision == Decision.Bet3 or
                                                 decision == Decision.Bet4):
                    return Decision.CheckRaise

                elif curr == Decision.Check and decision == Decision.Allin:
                    return Decision.CheckAllin

                elif curr == Decision.Bet and (decision == Decision.Bet3 or
                                               decision == Decision.Bet4 or
                                               decision == Decision.Allin or
                                               decision == Decision.CallR or
                                               decision == Decision.Call3 or
                                               decision == Decision.Call4 or
                                               decision == Decision.CallA):
                    return decision

                elif curr == Decision.CheckRaise and (decision == Decision.Bet4 or
                                                      decision == Decision.Call3 or
                                                      decision == Decision.Call4):
                    return Decision.CheckRaise

                elif curr == Decision.CheckRaise and (decision == Decision.Allin or
                                                      decision == Decision.CallA):
                    return Decision.CheckAllin

                elif curr == Decision.Raise and (decision == Decision.Bet4 or
                                                 decision == Decision.Allin or
                                                 decision == Decision.Call3 or
                                                 decision == Decision.Call4 or
                                                 decision == Decision.CallA):
                    return decision

                elif curr == Decision.Bet3 and (decision == Decision.Bet4 or
                                                decision == Decision.Allin or
                                                decision == Decision.Call4 or
                                                decision == Decision.CallA):
                    return decision

                elif curr == Decision.Bet4 and (decision == Decision.Bet4 or
                                                decision == Decision.Allin or
                                                decision == Decision.Call4 or
                                                decision == Decision.CallA):
                    return decision

                elif curr == Decision.CheckCall and (decision == Decision.CallR or
                                                     decision == Decision.Call3 or
                                                     decision == Decision.Call4):
                    return decision

                elif curr == Decision.CheckCall and (decision == Decision.Bet3 or
                                                     decision == Decision.Bet4):
                    return Decision.CheckRaise

                elif curr == Decision.CheckCall and (decision == Decision.Allin or
                                                     decision == Decision.CallA):
                    return Decision.CheckAllin

                elif curr == Decision.CallR and (decision == Decision.Call3 or
                                                 decision == Decision.Call4):
                    return decision

                elif curr == Decision.CallR and decision == Decision.Bet4:
                    return Decision.CheckRaise

                elif curr == Decision.CallR and (decision == Decision.Allin or
                                                 decision == Decision.CallA):
                    return Decision.CheckAllin

                elif curr == Decision.Call3 and (decision == Decision.Call4 or
                                                 decision == Decision.Check):
                    return decision

                elif curr == Decision.Call3 and decision == Decision.Bet4:
                    return Decision.CheckRaise

                elif curr == Decision.Call3 and (decision == Decision.Allin or
                                                 decision == Decision.CallA):
                    return Decision.CheckAllin

                elif curr == Decision.Call4 and decision == Decision.Call4:
                    return decision

                elif curr == Decision.Call4 and decision == Decision.Bet4:
                    return Decision.CheckRaise

                elif curr == Decision.Call4 and (decision == Decision.Allin or
                                                 decision == Decision.CallA):
                    return Decision.CheckAllin

                else:
                    raise ValueError(f'Undefined behavior curr = {curr} decision = {decision}')

        def set(self, step: Step, result: Result,
                raise_counter: int, all_in: bool) -> None:

            if result == Result.Fold:
                decision = Decision.Fold

            elif result == Result.Check:
                decision = Decision.Check

            elif result == Result.Call:
                if all_in:
                    decision = Decision.CallA

                elif raise_counter == 1:
                    decision = Decision.CheckCall

                elif raise_counter == 2:
                    decision = Decision.CallR

                elif raise_counter == 3:
                    decision = Decision.Call3

                elif raise_counter >= 4:
                    decision = Decision.Call4

                else:
                    raise ValueError('Wrong call decision when raise counter == 0')

            elif result == Result.Raise:
                if raise_counter == 0:
                    decision = Decision.Bet

                elif raise_counter == 1:
                    decision = Decision.Raise

                elif raise_counter == 2:
                    decision = Decision.Bet3

                elif raise_counter >= 3:
                    decision = Decision.Bet4

                else:
                    raise ValueError('Wrong raise counter')

            elif result == Result.Allin:
                decision = Decision.Allin

            else:
                raise ValueError(f'Wrong result id {result}')

            if step == Step.Preflop:
                self.preflop = self.decide(self.preflop, decision)

            elif step == Step.Flop:
                self.flop = self.decide(self.flop, decision)

            elif step == Step.Turn:
                self.turn = self.decide(self.turn, decision)

            elif step == Step.River:
                self.river = self.decide(self.river, decision)

            else:
                raise ValueError(f'Undefined step id {step}')

    def __init__(self, _id: int, name: str, money: int, controlled: bool, is_dummy: bool = False):

        self.id: int = _id
        self.name: str = name
        self.money: int = money
        self.money_last_time: int = money
        self.gived: int = 0
        self.in_pot: int = 0
        self.wins: int = 0
        self.in_game: bool = False
        self.in_play: bool = True
        self.re_seat: 'Players' = None
        self.cards: CardsPair = CardsPair()
        self.history: Player.History = Player.History()
        self.hand: Hand = None
        self.controlled: bool = controlled
        self.lose_time: int = None

        if not self.controlled:
            self.play: Play = PlayManager.get_play()
            self.name: str = str(self.play)

        else:
            self.play: Play = Play()
            self.network: Network = Network('py', f'{self.name} {self.id}', is_dummy)

    def __str__(self):

        return f'player {self.name} with {self.money} stack and {self.get_cards()}'

    def get_cards(self) -> str:

        return str(self.cards)

    def pay(self, money: int) -> int:

        self.money -= money - self.gived
        self.gived = money

        return money

    def pay_blind(self, money: int) -> int:

        return self.pay(min(money, self.money))

    def pay_ante(self, money: int) -> int:

        self.pay(min(money, self.money))
        return self.move_money_to_pot()

    def move_money_to_pot(self) -> int:

        self.in_pot += self.gived
        paid = self.gived
        self.gived = 0
        return paid

    def drop_cards(self) -> None:

        self.cards.drop()

    def fold(self) -> None:

        self.drop_cards()
        self.in_game = False

    def remaining_money(self) -> int:

        return self.money + self.gived

    def go_all_in(self) -> int:

        return self.pay(self.remaining_money())

    def in_all_in(self) -> bool:

        return self.in_game and self.money == 0

    def in_game_not_in_all_in(self) -> bool:

        return self.in_game and self.money > 0

    def add_card(self, card: Card) -> None:

        self.cards.set(card)

    def was_resit(self) -> None:

        self.re_seat = None

    def can_resit(self) -> bool:

        return self.re_seat is None

    def wait_to_resit(self) -> bool:

        return self.re_seat is not None

    def win_without_showdown(self, step: Step) -> None:

        self.play.wins_before_showdown += 1

        if step == Step.Preflop:
            self.play.preflop.wins += 1

        elif step == Step.Flop:
            self.play.flop.wins += 1

        elif step == Step.Turn:
            self.play.turn.wins += 1

        elif step == Step.River:
            self.play.river.wins += 1

        else:
            raise ValueError(f'Undefined step id {step}')

    def save_decisions(self) -> None:

        self.play.total_hands += 1

        for step in Step:

            if step == Step.Preflop:
                curr = self.history.preflop
                play = self.play.preflop

            elif step == Step.Flop:
                curr = self.history.flop
                play = self.play.flop

            elif step == Step.Turn:
                curr = self.history.turn
                play = self.play.turn

            else:
                curr = self.history.river
                play = self.play.river

            if curr is not None:
                play.add(curr)

        self.history.drop()

    def set_lose_time(self, stack: int = 0, place: int = 0) -> None:

        self.lose_time = int(datetime.now().timestamp() * 10 ** 6) * 10 ** 2 + stack * 10 + place

    def decide(self, step: Step, to_call: int, can_raise_from: int,
               cards: Card.Cards, online: bool) -> Result:

        if not self.in_game:
            return Result.DoNotPlay

        if self.money == 0 and self.in_game:
            return Result.InAllin

        if self.controlled:
            return self.input_decision(step, to_call, can_raise_from, cards)

        if step == Step.Preflop:
            curr_play: BasePlay = self.play.preflop

        elif step == Step.Flop:
            curr_play: BasePlay = self.play.flop

        elif step == Step.Turn:
            curr_play: BasePlay = self.play.turn

        elif step == Step.River:
            curr_play: BasePlay = self.play.river

        else:
            raise ValueError(f'Undefined step id {step}')

        if self.remaining_money() > can_raise_from * 3 and random() < curr_play.bluff:
            bluff = int(can_raise_from * (1 + random()))
            self.pay(bluff)
            Debug.decision(f'609 {self.name} raise bluff {bluff}; bluff = {curr_play.bluff}')

            if online:
                sleep(uniform(0.5, uniform(1, 2)))

            return Result.Raise

        probability = Poker.probability(self.cards, cards)

        if probability < curr_play.min_probability_to_play:

            if to_call == 0 or to_call == self.gived:
                Debug.decision(f'617 {self.name} check on low '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'to call = {to_call} self.gived = {self.gived}')

                if online:
                    sleep(uniform(0.5, 1))

                return Result.Check

            else:
                self.fold()
                Debug.decision(f'624 {self.name} fold low probability; '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_play}')

                if online:
                    sleep(uniform(0.5, 1))

                return Result.Fold

        if probability > curr_play.min_probability_to_all_in and random() < curr_play.probability_to_all_in:
            self.go_all_in()

            if self.remaining_money() <= to_call:
                Debug.decision(f'630 {self.name} call all in {self.gived} on high '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(1, uniform(1.5, 3)))

                return Result.Call

            else:
                Debug.decision(f'631 {self.name} all in {self.gived} on high '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(1, uniform(1.5, 3)))

                return Result.Allin

        bet = int(min(probability * curr_play.bet_, 1) * self.remaining_money())

        if bet == self.remaining_money():
            self.go_all_in()

            if self.remaining_money() <= to_call:
                Debug.decision(f'632 {self.name} call all in {self.gived} on high bet '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(2, uniform(3, 5)))

                return Result.Call

            else:
                Debug.decision(f'640 {self.name} all in {self.gived} on high bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet}')

                if online:
                    sleep(uniform(2, uniform(3, 5)))

                return Result.Allin

        if to_call > bet:

            if to_call == 0 or self.gived == to_call:
                Debug.decision(f'643 {self.name} check while can not raise bet = {bet}')

                if online:
                    sleep(uniform(0.5, uniform(1, 3)))

                return Result.Check

            else:
                self.fold()
                Debug.decision(f'647 {self.name} fold on low bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(1, uniform(2, 4)))

                return Result.Fold

        if can_raise_from > bet:

            if to_call == 0 or self.gived == to_call:
                Debug.decision(f'656 {self.name} check on mid bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(0.5, uniform(1, 2)))

                return Result.Check

            else:
                self.pay(to_call)
                Debug.decision(f'666 {self.name} call {to_call} on mid bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(2, uniform(4, 6)))

                return Result.Call

        else:

            raise_bet = int(min(probability * curr_play.bet_ * curr_play.reduced_raise, 1) * self.remaining_money())

            if raise_bet <= self.gived:

                if to_call == 0 or self.gived == to_call:
                    Debug.decision(f'670 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return Result.Check

                else:
                    self.fold()
                    Debug.decision(f'672 {self.name} fold while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Fold

            if raise_bet < to_call:

                if to_call == 0 or self.gived == to_call:
                    Debug.decision(f'673 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return Result.Check

                else:
                    self.fold()
                    Debug.decision(f'677 {self.name} fold while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Fold

            if raise_bet < can_raise_from:

                if to_call == 0 or to_call == self.gived:
                    Debug.decision(f'656 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(0.5, uniform(1, 2)))

                    return Result.Check

                else:
                    self.pay(to_call)
                    Debug.decision(f'682 {self.name} call {to_call} while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(3, uniform(6, 8)))

                    return Result.Call

            if raise_bet == self.remaining_money():

                self.go_all_in()

                if raise_bet <= to_call:
                    Debug.decision(f'684 {self.name} call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Call

                else:
                    Debug.decision(f'687 {self.name} all in {self.gived} while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return Result.Allin

            if to_call == 0 and random() < curr_play.check_:
                Debug.decision(f'690 {self.name} cold check wanted to raise {raise_bet} '
                               f'check probability {curr_play.check}')

                if online:
                    sleep(uniform(0.5, uniform(1, 2)))

                return Result.Check

            elif to_call != 0 and random() < curr_play.call:

                if self.remaining_money() <= to_call:
                    self.go_all_in()
                    Debug.decision(f'691 {self.name} cold call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Call

                else:
                    self.pay(to_call)
                    Debug.decision(f'692 {self.name} cold call {to_call} while wanted to raise {raise_bet} '
                                   f'call probability {curr_play.call}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Call

            if self.remaining_money() <= raise_bet:

                self.go_all_in()

                if self.remaining_money() <= to_call:
                    Debug.decision(f'693 {self.name} call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Call

                else:
                    Debug.decision(f'694 {self.name} raise all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Result.Allin

            else:
                self.pay(raise_bet)
                Debug.decision(f'695 {self.name} raise {raise_bet} on high bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(3, uniform(6, 9)))

                return Result.Raise

    def input_decision(self, step: Step, to_call: int, min_raise: int, cards: Card.Cards) \
            -> Result:

        Debug.input_decision()
        Debug.input_decision(f'you have {self.get_cards()}')
        if step != Step.Preflop:
            Debug.input_decision(f'on table {Card.str(cards)}')
            Debug.input_decision(f'your combination: {Poker.max_strength(self.cards.get() + cards)}')
        Debug.input_decision(f'probability to win: {Poker.probability(self.cards, cards)}')

        outs, outs_cards = Poker.calculate_outs(self.cards, cards)

        Debug.input_decision(f'outs: {outs} - {" ".join([card.card for card in outs_cards])}')
        Debug.input_decision()

        available_decisions = [(Result.Fold,)]

        Debug.input_decision('1 - fold')
        if self.remaining_money() > to_call:
            if to_call == 0 or self.gived == to_call:
                available_decisions += [(Result.Check,)]
                Debug.input_decision(f'2 - check')
            else:
                available_decisions += [(Result.Call, to_call)]
                Debug.input_decision(f'2 - call {to_call} you called {self.gived} remains {to_call - self.gived}')

            if min_raise < self.remaining_money():
                available_decisions += [(Result.Raise, min_raise, self.remaining_money())]
                Debug.input_decision(f'3 - raise from {min_raise} to {self.remaining_money()}')
            else:
                available_decisions += [(Result.Allin, self.remaining_money())]
                Debug.input_decision(f'3 - all in {self.remaining_money()} you called '
                                     f'{self.gived} remains {self.money}')

        else:
            available_decisions += [(Result.Call, self.remaining_money())]
            Debug.input_decision(f'2 - call all in {self.remaining_money()}')

        while True:
            answer = self.network.input_decision(available_decisions)
            try:
                if answer[0] == '1':
                    self.fold()
                    return Result.Fold

                elif answer[0] == '2':
                    if self.remaining_money() > to_call:
                        if to_call == 0 or self.gived == to_call:
                            return Result.Check
                        else:
                            self.pay(to_call)
                            return Result.Call
                    else:
                        self.go_all_in()
                        return Result.Call

                elif answer[0] == '3':

                    if self.remaining_money() > to_call:

                        if len(answer) == 2:

                            raised_money = int(answer[1])

                            if raised_money == self.remaining_money():
                                self.go_all_in()
                                return Result.Allin

                            if raised_money < min_raise:
                                raise IndexError

                            if raised_money > self.remaining_money():
                                raise IndexError

                            self.pay(raised_money)
                            return Result.Raise

                        else:
                            self.go_all_in()
                            return Result.Allin

            except IndexError:
                continue
            else:
                break

        self.fold()
        return Result.Fold
