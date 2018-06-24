from __future__ import annotations
from typing import List, Iterator, Optional
from threading import Lock
from time import sleep
from holdem.player.player import Player
from holdem.delay import Delay
from holdem.network import Network


class Players:

    def __init__(self, game, seats: int, _id: int, is_final: bool):
        
        self.game = game
        self.players: TablePlayers = [None] * seats
        self.controlled: TablePlayers = []
        self.network: Network = None
        self.online: bool = False

        self.id = _id
        self.curr_player: int = -1
        self.curr_seat: int = -1
        self.button: int = -1
        self.wait_to_sit: int = 0
        self.wait_to_leave: int = 0
        self.total_seats: int = seats
        self.count: int = 0
        self.is_final: bool = is_final
        self.lock: Lock = Lock()

    def move_button(self) -> None:

        if self.to_button() is None and self.count == 2:
            self.button = (self.button + 1) % self.total_seats
            while self.players[self.button] is None:
                self.button = (self.button + 1) % self.total_seats

        self.button = (self.button + 1) % self.total_seats
        while self.players[self.button] is None:
            self.button = (self.button + 1) % self.total_seats

    def get_curr_seat(self) -> Player:

        return self.players[self.curr_seat]

    def is_seat_free(self) -> bool:

        return self.players[self.curr_seat] is None

    def is_seat_busy(self) -> bool:

        return self.players[self.curr_seat] is not None

    def get_curr_player(self) -> Player:

        return self.players[self.curr_player]

    def next_seat(self) -> Player:

        self.curr_seat = (self.curr_seat + 1) % self.total_seats
        return self.players[self.curr_seat]

    def next_free_seat(self) -> None:

        self.curr_seat = (self.curr_seat + 1) % self.total_seats
        while self.players[self.curr_seat] is not None:
            self.curr_seat = (self.curr_seat + 1) % self.total_seats

    def next_busy_seat(self) -> Player:

        self.curr_seat = (self.curr_seat + 1) % self.total_seats
        while self.players[self.curr_seat] is None:
            self.curr_seat = (self.curr_seat + 1) % self.total_seats

        return self.players[self.curr_seat]

    def next_player(self) -> Player:

        self.curr_player = (self.curr_player + 1) % self.total_seats
        while self.players[self.curr_player] is None:
            self.curr_player = (self.curr_player + 1) % self.total_seats

        return self.players[self.curr_player]

    def seat_to_player(self) -> Player:

        self.curr_seat = self.curr_player
        return self.players[self.curr_seat]

    def to_button(self) -> Player:

        self.curr_player = self.button
        return self.players[self.curr_player]

    def get_button(self) -> Player:

        return self.players[self.button]

    def to_button_seat(self) -> Player:

        self.curr_seat = self.button
        return self.players[self.curr_seat]

    def to_small_blind(self) -> Player:

        if self.count == 2:
            return self.to_button()
        else:
            self.curr_player = self.button
            return self.next_player()

    def to_big_blind(self) -> Player:
        self.to_small_blind()
        return self.next_player()

    def all_players(self) -> Iterator[Player]:

        for player in self.players:
            if player is not None:
                yield player

    def in_game_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if player.in_game:
                yield player

    def not_in_game_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if not player.in_game:
                yield player

    def count_in_game_players(self) -> int:

        count = 0
        for _ in self.in_game_players():
            count += 1
        return count

    def all_in_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if player.in_all_in():
                yield player

    def in_game_not_in_all_in_players(self) -> Iterator[Player]:

        for player in self.all_players():
            if player.in_game_not_in_all_in():
                yield player

    def count_all_in_players(self) -> int:

        count = 0
        for _ in self.all_in_players():
            count += 1
        return count

    def length_to_button(self, player: Player) -> int:

        save_curr_player = self.curr_player
        length = 0

        self.to_button()
        while self.next_player() != player:
            length += 1

        self.curr_player = save_curr_player
        return length

    def sort_by_nearest_to_button(self, players: TablePlayers) -> TablePlayers:

        return sorted(players, key=lambda p: self.length_to_button(p))

    def player_position(self, player: Player) -> str:

        if self.count == 2:
            return 'D/SB' if self.to_button() == player else ' BB '

        curr = self.to_button()
        if player == curr:
            return '  D '

        curr = self.next_player()
        if player == curr:
            return ' SB '

        curr = self.next_player()
        if player == curr:
            return ' BB '

        return '    '

    def sit_player(self, player: Player, from_other_table) -> None:

        if self.is_seat_busy():
            raise IndexError(f'Can not sit {player.name}: on this seat sits {self.get_curr_seat().name}')

        self.players[self.curr_seat] = player

        if self.online:
            self.network.add_player(player, self.curr_seat)
            sleep(Delay.AddPlayer)

        if player.controlled:
            self.controlled += [player]
            player.network.resit(player, self)

        self.count += 1

        if from_other_table:

            self.wait_to_sit -= 1

            player.re_seat.wait_to_leave -= 1

            player.was_resit()

    def add_player(self, player: Player, from_other_table: bool = True) -> None:

        if self.count == self.total_seats:
            raise OverflowError(f'Can not sit {player.name}: {self.count} sits on this table')

        if from_other_table and self.wait_to_sit == 0:
            raise ValueError(f'Can not sit {player.name}: table was not notified')

        with self.lock:

            if self.count == 0:
                self.button = 0
                self.to_button_seat()
                self.sit_player(player, from_other_table)

            elif self.count == 1:

                self.to_button_seat()
                self.next_free_seat()
                self.sit_player(player, from_other_table)

            else:
                self.to_button_seat()

                for _ in range(2):
                    self.next_seat()
                    while self.is_seat_free():
                        self.next_seat()

                self.next_free_seat()
                self.sit_player(player, from_other_table)

    def remove_player(self, players: Players) -> None:

        if self.count == 0:
            raise ValueError('No one to remove')

        self.to_big_blind()

        while self.get_curr_player().wait_to_resit():
            self.next_player()

        self.get_curr_player().re_seat = players

        self.wait_to_leave += 1

        players.wait_to_sit += 1

    def delete_player(self, player: Player) -> None:

        self.players[self.players.index(player)] = None

        if player in self.controlled:
            del self.controlled[self.controlled.index(player)]

        self.count -= 1

        if self.online:
            self.network.delete_player(player)
            sleep(Delay.DeletePlayer)

    def resit_all_needed_players(self) -> None:

        for player in self.all_players():
            if player.wait_to_resit():
                self.delete_player(player)
                player.re_seat.add_player(player)

    def remove_losers(self, game) -> None:

        losers: List[Player] = []

        for player in self.all_players():
            if player.money == 0:

                losers += [player]
                player.in_play = False

            else:
                player.money_last_time = player.money

        loser_stacks = sorted(player.money_last_time for player in losers)
        loser_sits = sorted([self.length_to_button(player) for player in losers], reverse=True)

        for loser in losers:
            loser.set_lose_time(loser_stacks.index(loser.money_last_time),
                                loser_sits.index(self.length_to_button(loser)))

        for loser in losers:

            if loser.controlled:
                loser.network.busted(game.find_place(loser))

            else:
                loser.play.busy = False

            self.delete_player(loser)

    def __str__(self):

        return '\n'.join('     Empty seat' if p is None else
                         f'{self.player_position(p)} {p.get_cards()} {p.name} money = {p.money}'
                         for p in self.players)


TablePlayers = List[Optional[Player]]
