from typing import List
from data.game_model.poker_event import Event, PokerEvent
from data.game_model.mock_player import MockPlayer
from data.game_model.observer_player import ObserverPlayer
from core.cards.deck import Deck, Card
from core.cards.cards_pair import CardsPair
from holdem.board import Board
from holdem.play.step import Step


class PokerHand:

    def __init__(self, players: List[MockPlayer]):
        self.id: int = 0
        self.players: List[MockPlayer] = players
        self.sit_during_game: List[MockPlayer] = None
        self.preflop: List[PokerEvent] = []
        self.flop: List[PokerEvent] = []
        self.turn: List[PokerEvent] = []
        self.river: List[PokerEvent] = []
        self.small_blind: int = 0
        self.big_blind: int = 0
        self.ante: int = 0
        self.total_pot: int = 0
        self.table_id: int = 0
        self.button_seat: int = 0
        self.players_left: int = 0
        self.is_final: bool = False
        self.goes_to_showdown: bool = False
        self.board: Board = Board(Deck())
        self.curr_step: Step = Step.Preflop
        self.curr_events: List[PokerEvent] = self.preflop

    def init(self, hand_id, sb, bb, out_of_hand, table_num, button):
        self.id = hand_id
        self.small_blind = sb
        self.big_blind = bb
        self.sit_during_game = out_of_hand
        self.table_id = table_num
        self.button_seat = button

    def add_winner(self, name: str) -> None:
        self.get_player(name).is_winner = True

    def get_winners(self) -> List[MockPlayer]:
        return [player for player in self.players if player.is_winner]

    def get_losers(self) -> List[MockPlayer]:
        return [player for player in self.players if player.is_loser]

    def add_loser(self, name: str) -> None:
        self.get_player(name).is_loser = True

    def set_flop_cards(self, card1: Card, card2: Card, card3: Card) -> None:
        self.board.set_flop_cards(card1, card2, card3)

    def set_turn_card(self, card: Card) -> None:
        self.board.set_turn_card(card)

    def set_river_card(self, card: Card) -> None:
        self.board.set_river_card(card)

    def set_cards(self, name: str, cards: CardsPair) -> None:
        player = self.get_player(name)
        if player.cards is None:
            player.cards = cards
        elif player.cards.second is not None and cards.second is None and cards.first in player.cards.get():
            # means that player cards is already known but he show only one card to everyone else
            return
        elif player.cards != cards:
            raise ValueError(f'Player {name} firstly has {player.cards} '
                             f'then {cards} in one hand')

    def get_player(self, name: str) -> MockPlayer:
        return max(player for player in self.players if player.name == name)

    def add_decision(self, name: str, event: Event, money: int, msg: str = '') -> None:
        if event == Event.ObserverChatMessage:
            self.curr_events += [PokerEvent(ObserverPlayer(name), event, money, msg)]
        else:
            player = self.get_player(name)
            self.curr_events += [PokerEvent(player, event, money, msg)]
            player.add_decision(self.curr_step, event, money)

    def set_all_in(self, name: str) -> None:
        self.get_player(name).is_all_in = True

    def get_only_all_in(self) -> str:
        return max(player for player in self.players if player.is_all_in).name

    def switch_to_step(self, step: Step) -> None:

        self.curr_step = step

        if step == Step.Preflop:
            self.curr_events = self.preflop
        elif step == Step.Flop:
            self.curr_events = self.flop
        elif step == Step.Turn:
            self.curr_events = self.turn
        elif step == Step.River:
            self.curr_events = self.river
        else:
            raise ValueError('No such step id ' + str(step))

    def next_step(self) -> None:
        self.switch_to_step(Step.next_step(self.curr_step))

    def __str__(self) -> str:

        ret = [f'    Small blind: {self.small_blind}']
        ret += [f'    Big blind: {self.big_blind}']
        ret += [f'    Ante: {self.ante}']
        ret += [f'    Players left: {self.players_left}']
        ret += [f'    Total pot: {self.total_pot}']

        ret += ['    Players:']
        for player in self.players:
            ret += [f'        {player.name} : {player.money} : '
                    f'{player.cards if player.cards is not None else "?? ??"} '
                    f'{"disconnected" if not player.is_active else ""}']

        if self.preflop:
            ret += ['    Preflop:']
            for event in self.preflop:
                ret += [' ' * 8 + str(event)]

        if self.flop:
            ret += [f'    Flop: {self.board.flop1.card} '
                    f'{self.board.flop2.card} '
                    f'{self.board.flop3.card}']
            for event in self.flop:
                ret += [' ' * 8 + str(event)]

        if self.turn:
            ret += [f'    Turn: {self.board.flop1.card} '
                    f'{self.board.flop2.card} '
                    f'{self.board.flop3.card} '
                    f'{self.board.turn.card}']
            for event in self.turn:
                ret += [' ' * 8 + str(event)]

        if self.river:
            ret += [f'    River: {self.board.flop1.card} '
                    f'{self.board.flop2.card} '
                    f'{self.board.flop3.card} '
                    f'{self.board.turn.card} '
                    f'{self.board.river.card}']
            for event in self.river:
                ret += [' ' * 8 + str(event)]

        ret += [f'    Board: {self.board}']

        winners = self.get_winners()
        losers = self.get_losers()

        if winners:
            ret += [f'    Winners:']
            for winner in winners:
                ret += [' ' * 8 + winner.name]

        if losers:
            ret += [f'    Losers:']
            for loser in losers:
                ret += [' ' * 8 + loser.name]

        return '\n'.join(ret)
