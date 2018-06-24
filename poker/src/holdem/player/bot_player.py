from time import sleep
from typing import Tuple
from random import random, uniform
from core.cards.card import Cards
from holdem.player.player import Player
from holdem.play.play import Play
from holdem.play.play_manager import PlayManager
from holdem.play.step import Step
from holdem.play.option import Option
from holdem.play.base_play import BasePlay
from holdem.poker.holdem_poker import HoldemPoker
from holdem.base_network import BaseNetwork
from special.debug import Debug
from special.settings import Settings
from special.mode import Mode


class BotPlayer(Player):
    def __init__(self, _id: int, money: int):
        play: Play = PlayManager.get_play(Settings.game_mode == Mode.Testing)
        super().__init__(_id, money, False, str(play), play, BaseNetwork())

    def _decide(self, *,
                step: Step,
                to_call: int,
                min_raise: int,
                board: Cards,
                online: bool,
                **_) -> Tuple[Option, int]:

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

        if self.remaining_money() > min_raise * 3 and random() < curr_play.bluff:
            bluff = int(min_raise * (1 + random()))

            Debug.decision(f'609 {self.name} raise bluff {bluff}; bluff = {curr_play.bluff}')

            if online:
                sleep(uniform(0.5, uniform(1, 2)))

            return Option.Raise, bluff

        probability = HoldemPoker.probability(self.cards, board)

        if probability < curr_play.min_probability_to_play:

            if to_call == 0 or to_call == self.gived:
                Debug.decision(f'617 {self.name} check on low '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'to call = {to_call} self.gived = {self.gived}')

                if online:
                    sleep(uniform(0.5, 1))

                return Option.CheckCall, 0

            else:
                Debug.decision(f'624 {self.name} fold low probability; '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_play}')

                if online:
                    sleep(uniform(0.5, 1))

                return Option.Fold, 0

        if probability > curr_play.min_probability_to_all_in and random() < curr_play.probability_to_all_in:

            if self.remaining_money() <= to_call:
                Debug.decision(f'630 {self.name} call all in {self.gived} on high '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(1, uniform(1.5, 3)))

            else:
                Debug.decision(f'631 {self.name} all in {self.gived} on high '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(1, uniform(1.5, 3)))

            return Option.Raise, self.remaining_money()

        bet = int(min(probability * curr_play.bet_, 1) * self.remaining_money())

        if bet == self.remaining_money():

            if self.remaining_money() <= to_call:
                Debug.decision(f'632 {self.name} call all in {self.gived} on high bet '
                               f'prob = {probability}; '
                               f'min = {curr_play.min_probability_to_all_in}')

                if online:
                    sleep(uniform(2, uniform(3, 5)))

            else:
                Debug.decision(f'640 {self.name} all in {self.gived} on high bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet}')

                if online:
                    sleep(uniform(2, uniform(3, 5)))

            return Option.Raise, bet

        if to_call > bet:

            if to_call == 0 or self.gived == to_call:
                Debug.decision(f'643 {self.name} check while can not raise bet = {bet}')

                if online:
                    sleep(uniform(0.5, uniform(1, 3)))

                return Option.CheckCall, 0

            else:
                Debug.decision(f'647 {self.name} fold on low bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(1, uniform(2, 4)))

                return Option.Fold, 0

        if min_raise > bet:

            if to_call == 0 or self.gived == to_call:
                Debug.decision(f'656 {self.name} check on mid bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(0.5, uniform(1, 2)))

                return Option.CheckCall, 0

            else:
                Debug.decision(f'666 {self.name} call {to_call} on mid bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(2, uniform(4, 6)))

                return Option.CheckCall, to_call

        else:

            raise_bet = int(min(probability * curr_play.bet_ * curr_play.reduced_raise, 1) * self.remaining_money())

            if raise_bet <= self.gived:

                if to_call == 0 or self.gived == to_call:
                    Debug.decision(f'670 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return Option.CheckCall, 0

                else:
                    Debug.decision(f'672 {self.name} fold while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Option.Fold, 0

            if raise_bet < to_call:

                if to_call == 0 or self.gived == to_call:
                    Debug.decision(f'673 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                    return Option.CheckCall, 0

                else:
                    Debug.decision(f'677 {self.name} fold while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Option.Fold, 0

            if raise_bet < min_raise:

                if to_call == 0 or to_call == self.gived:
                    Debug.decision(f'656 {self.name} check while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(0.5, uniform(1, 2)))

                    return Option.CheckCall, 0

                else:
                    Debug.decision(f'682 {self.name} call {to_call} while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(3, uniform(6, 8)))

                    return Option.CheckCall, to_call

            if raise_bet == self.remaining_money():

                if raise_bet <= to_call:
                    Debug.decision(f'684 {self.name} call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                else:
                    Debug.decision(f'687 {self.name} all in {self.gived} while thinks about raise {raise_bet}')

                    if online:
                        sleep(uniform(1, uniform(2, 3)))

                return Option.Raise, raise_bet

            if to_call == 0 and random() < curr_play.check_:
                Debug.decision(f'690 {self.name} cold check wanted to raise {raise_bet} '
                               f'check probability {curr_play.check}')

                if online:
                    sleep(uniform(0.5, uniform(1, 2)))

                return Option.CheckCall, 0

            elif to_call != 0 and random() < curr_play.call:

                if self.remaining_money() <= to_call:
                    Debug.decision(f'691 {self.name} cold call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Option.CheckCall, self.remaining_money()

                else:
                    Debug.decision(f'692 {self.name} cold call {to_call} while wanted to raise {raise_bet} '
                                   f'call probability {curr_play.call}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                    return Option.CheckCall, to_call

            if self.remaining_money() <= raise_bet:

                if self.remaining_money() <= to_call:
                    Debug.decision(f'693 {self.name} call all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                else:
                    Debug.decision(f'694 {self.name} raise all in {self.gived}')

                    if online:
                        sleep(uniform(2, uniform(4, 6)))

                return Option.Raise, self.remaining_money()

            else:
                Debug.decision(f'695 {self.name} raise {raise_bet} on high bet '
                               f'prob = {probability}; '
                               f'bet coefficient = {curr_play.bet} '
                               f'bet = {bet}')

                if online:
                    sleep(uniform(3, uniform(6, 9)))

                return Option.Raise, raise_bet
