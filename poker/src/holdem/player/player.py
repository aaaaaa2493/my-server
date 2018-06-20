from typing import List, Dict
from datetime import datetime
from holdem.play.decision import Decision
from holdem.play.step import Step
from holdem.play.result import Result
from holdem.poker.hand import Hand
from core.cards.cards_pair import CardsPair
from holdem.play.play import Play
from holdem.base_network import BaseNetwork
from core.cards.card import Card
from data.game_model.poker_position import PokerPosition
from data.game_model.player_statistics import PlayerStatistics


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
                self.preflop: Decision = Decision.update(self.preflop, decision)

            elif step == Step.Flop:
                self.flop: Decision = Decision.update(self.flop, decision)

            elif step == Step.Turn:
                self.turn: Decision = Decision.update(self.turn, decision)

            elif step == Step.River:
                self.river: Decision = Decision.update(self.river, decision)

            else:
                raise ValueError(f'Undefined step id {step}')

    def __init__(self, _id: int, money: int, controlled: bool, name: str, play: Play, net: BaseNetwork):

        self.id: int = _id
        self.name: str = name
        self.money: int = money
        self.money_last_time: int = money
        self.gived: int = 0
        self.in_pot: int = 0
        self.wins: int = 0
        self.in_game: bool = False
        self.in_play: bool = True
        self.re_seat: Players = None
        self.cards: CardsPair = CardsPair()
        self.history: Player.History = Player.History()
        self.hand: Hand = None
        self.controlled: bool = controlled
        self.lose_time: int = None
        self.play: Play = play
        self.network: BaseNetwork = net
        self.position: PokerPosition = None
        self.folds: Dict[PokerPosition, PlayerStatistics] = {
            PokerPosition.Blinds: PlayerStatistics(),
            PokerPosition.Early: PlayerStatistics(),
            PokerPosition.Middle: PlayerStatistics(),
            PokerPosition.Late: PlayerStatistics(),
        }
        self.calls: Dict[PokerPosition, PlayerStatistics] = {
            PokerPosition.Blinds: PlayerStatistics(),
            PokerPosition.Early: PlayerStatistics(),
            PokerPosition.Middle: PlayerStatistics(),
            PokerPosition.Late: PlayerStatistics(),
        }
        self.raises: Dict[PokerPosition, PlayerStatistics] = {
            PokerPosition.Blinds: PlayerStatistics(),
            PokerPosition.Early: PlayerStatistics(),
            PokerPosition.Middle: PlayerStatistics(),
            PokerPosition.Late: PlayerStatistics(),
        }
        self.checks: Dict[PokerPosition, PlayerStatistics] = {
            PokerPosition.Blinds: PlayerStatistics(),
            PokerPosition.Early: PlayerStatistics(),
            PokerPosition.Middle: PlayerStatistics(),
            PokerPosition.Late: PlayerStatistics(),
        }

    def __str__(self):

        return f'player {self.name} with {self.money} stack and {self.get_cards()}'

    def get_cards(self) -> str:

        return str(self.cards)

    def pay(self, money: int) -> int:

        money = min(money, self.remaining_money())

        self.money -= money - self.gived
        self.gived = money

        return money

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

    def make_decision(self, **kwargs) -> Result:
        if not self.in_game:
            return Result.DoNotPlay

        if self.money == 0 and self.in_game:
            return Result.InAllin

        return self.decide(**kwargs)

    def decide(self, **kwargs) -> Result:
        raise NotImplementedError('decide')
