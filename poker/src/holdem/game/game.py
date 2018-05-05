from threading import Thread
from random import shuffle, choice
from time import sleep
from statistics import mean
from typing import List
from os.path import exists
from pickle import load, dump
from core.base_game import BaseGame
from core.blinds.scheme.scheme import Scheme
from core.blinds.scheme.schemes import Schemes
from core.blinds.timed_blinds import TimedBlinds
from holdem.delay import Delay
from holdem.table import Table
from holdem.player.player import Player
from holdem.player.bot_player import BotPlayer
from holdem.player.real_player import RealPlayer
from holdem.player.neural_network.base_neural_network_player import NeuralNetworkClass
from holdem.play.play import Play
from holdem.network import Network
from special.debug import Debug
from special.settings import Settings
from special.mode import Mode


class Game(BaseGame):

    def __init__(self, id_: int = 0, players: int = 9, seats: int = 9, start_stack: int = 15000,
                 blinds: Scheme = Schemes.WSOP.value):

        super().__init__(id_, TimedBlinds(blinds, self))

        if players < 1:
            raise ValueError("Can not be players less than one in new game")

        self.next_id: int = 0
        self.thread: Thread = None
        self.resitting_thread: Thread = None
        self.start_stack: int = start_stack
        self.total_players: int = players
        self.total_seats: int = seats
        self.total_tables: int = (players - 1) // seats + 1
        self.players_count: int = 0
        self.players: List[Player] = []

        if self.total_tables == 1:
            self.tables: Table.Tables = [Table(self, 0, seats, self.blinds, True)]
            self.final_table = self.tables[0]

        else:
            self.tables: Table.Tables = [Table(self, _id, seats, self.blinds, False)
                                         for _id in range(1, self.total_tables + 1)]
            self.final_table = Table(self, 0, self.total_seats, self.blinds, True)

        self.average_stack: int = None
        self.players_left: int = None
        self.top_9: List[Player] = None

    def add_nn_player(self, path: str, net_class: NeuralNetworkClass) -> bool:
        return self.add_player(net_class(self.next_id, self.start_stack, path))

    def add_real_player(self, name: str) -> bool:
        return self.add_player(RealPlayer(self.id, self.next_id, name, self.start_stack))

    def add_bot_player(self) -> bool:
        return self.add_player(BotPlayer(self.next_id, self.start_stack))

    def add_player(self, player: Player) -> bool:

        if self.players_count == self.total_players:
            raise OverflowError(f'Player limit reached max = {self.total_players}')

        self.next_id += 1

        self.players += [player]
        self.players_count += 1

        if self.players_count == self.total_players:
            self.thread = Thread(target=self.start_game, name='Game infinite')
            self.thread.start()
            return True

        return False

    def delete_player(self, name) -> None:

        if name in [player.name for player in self.players]:
            player_to_delete = max(player for player in self.players if name == player.name)

            del self.players[self.players.index(player_to_delete)]
            del player_to_delete

            self.players_count -= 1

    def start_game(self) -> None:

        if any(player.controlled for player in self.players) or self.online:

            self.online = True
            Play.ExtendedName = False

            for table in self.tables:
                table.network = Network({'type': 'tb', 'name': str(table.id), 'id': self.id})
                table.online = True

                table.players.network = table.network
                table.players.online = True

        else:
            Play.ExtendedName = True

        shuffle(self.players)
        for player in self.players:
            min_count_players_on_table = min(table.players.count for table in self.tables)
            tables_with_min_count = [table for table in self.tables if
                                     table.players.count == min_count_players_on_table]
            found_table: Table = choice(tables_with_min_count)
            found_table.players.add_player(player, False)

        self.game_started = True

        self.infinite()

    def do_one_hand(self) -> None:

        if self.blinds.next_hand():
            Debug.game_progress(f'Blinds are: {self.blinds.small_blind} '
                                f'{self.blinds.big_blind} {self.blinds.ante}')

        Debug.game_progress(f'Start hand {self.tables[0].board.hand} tables = {len(self.tables)} '
                            f'players = {sum(table.players.count for table in self.tables)}')

        for table in self.tables:
            table.run()

    def blinds_increased(self):

        Debug.game_progress(f'Blinds are: {self.blinds.small_blind} '
                            f'{self.blinds.big_blind} {self.blinds.ante}')

        small = self.blinds.small_blind
        big = self.blinds.big_blind
        ante = self.blinds.ante

        for table in self.tables:
            if table.online:
                table.network.blinds_increased(small, big, ante)
                sleep(Delay.BlindsIncreased)

    @staticmethod
    def get_first_free_table(tables: Table.Tables) -> Table:

        while True:

            for table in tables:

                if table.in_game or table.wait:
                    continue

                else:
                    with table.lock:

                        table.wait = True
                        return table
            sleep(0.01)

    def resit_players(self) -> None:

        total_players = sum(table.players.count for table in self.tables)

        if self.total_seats * len(self.tables) - total_players >= self.total_seats:
            Debug.resitting(f'Start to delete tables total tables = {len(self.tables)} '
                            f'seats = {self.total_seats * len(self.tables)} '
                            f'players = {total_players} '
                            f'difference = {self.total_seats * len(self.tables) - total_players}')

        while self.total_seats * len(self.tables) - total_players >= self.total_seats:

            if len(self.tables) == 2:

                self.tables[0].wait = True
                self.tables[1].wait = True

                while self.tables[0].in_game or self.tables[1].in_game:
                    sleep(0.01)

                last_players = [player for table in self.tables for player in table.players.all_players()]
                shuffle(last_players)
                final_table = self.final_table

                if self.online:
                    final_table.network = Network({'type': 'tb', 'name': '0', 'id': self.id})
                    final_table.online = True
                    final_table.players.network = final_table.network
                    final_table.players.online = True

                for player in last_players:
                    final_table.players.add_player(player, False)

                Debug.resitting('Resit all players to final table')

                if self.tables[0].online:
                    self.tables[0].network.end()

                if self.tables[1].online:
                    self.tables[1].network.end()

                self.tables = [final_table]
                return

            if self.online:
                table_to_remove: Table = self.get_first_free_table(self.tables)

            else:
                table_to_remove: Table = choice(self.tables)

            while table_to_remove.in_game:
                sleep(0.01)

            while table_to_remove.players.count:
                other_min_count = min(table.players.count for table in self.tables if table != table_to_remove)

                other_tables_with_min_count = [table for table in self.tables if table != table_to_remove and
                                               table.players.count == other_min_count]

                table_to_resit: Table = choice(other_tables_with_min_count)

                Debug.resitting(f'Resit player from removing table {table_to_remove.id} '
                                f'count = {table_to_remove.players.count}'
                                f' to table {table_to_resit.id} count = {table_to_resit.players.count}')

                table_to_remove.players.remove_player(table_to_resit.players)
                table_to_remove.players.resit_all_needed_players()

            if table_to_remove.players.count != 0:
                raise ValueError(f'Try to delete table {table_to_remove.id} with players in it')

            Debug.resitting(f'Delete table {table_to_remove.id}')

            del self.tables[self.tables.index(table_to_remove)]

            if table_to_remove.online:
                table_to_remove.network.end()

            del table_to_remove

            if self.online:
                return

        counts = [table.players.count for table in self.tables]
        max_counts = max(counts)
        min_counts = min(counts)

        if max_counts - min_counts > 1:
            Debug.resitting(f'Start to resit without deleting tables max = {max_counts} min = {min_counts} '
                            f'players = {sum(counts)} '
                            f'difference = {self.total_seats * len(self.tables) - sum(counts)}')

        while max_counts - min_counts > 1:

            tables_with_max_count = [table for table in self.tables if table.players.count == max_counts]
            tables_with_min_count = [table for table in self.tables if table.players.count == min_counts]

            table_to_resit: Table = choice(tables_with_min_count)

            if self.online:
                table_from_resit = self.get_first_free_table(tables_with_max_count)

            else:
                table_from_resit: Table = choice(tables_with_max_count)

            Debug.resitting(f'Resit player from table {table_from_resit.id} count = {table_from_resit.players.count}'
                            f' to table {table_to_resit.id} count = {table_to_resit.players.count}')

            table_from_resit.players.remove_player(table_to_resit.players)

            while table_from_resit.in_game:
                sleep(0.01)

            table_from_resit.players.resit_all_needed_players()

            table_from_resit.wait = False

            if self.online:
                return

            counts = [table.players.count for table in self.tables]
            max_counts = max(counts)
            min_counts = min(counts)

    def print_places(self) -> None:

        for player in self.players:
            if player.lose_time is None:
                player.set_lose_time()
                if player.controlled:
                    player.network.win()
                Debug.evolution(f'Game wins {player.name}')

        sorted_players = sorted(self.players, key=lambda p: p.lose_time, reverse=True)

        if not Debug.Standings:
            for place, player in enumerate(sorted_players[:10]):
                Debug.evolution(f'{place+1:>4}) {player.play}')

        if Settings.game_mode == Mode.Testing:
            if not exists('networks/plays'):
                plays = {}
            else:
                plays = load(open('networks/plays', 'rb'))

        for place, player in enumerate(sorted_players):
            Debug.standings(f'{place+1:>4}) {player.name}')
            if not player.controlled:
                player.play.set_place(place + 1, self.players_count)
            if Settings.game_mode == Mode.Testing:
                if player.play.exemplar == 0:
                    print('Net', player.play.name, ':', place + 1)
                if player.play.name in plays:
                    plays[player.play.name] += place + 1
                else:
                    plays[player.play.name] = place + 1

        if Settings.game_mode == Mode.Testing:
            dump(plays, open('networks/plays', 'wb'))

        self.game_finished = True

    def find_place(self, player: Player) -> int:

        if player.lose_time is not None:

            finished = sorted([player for player in self.players if player.lose_time is not None],
                              key=lambda p: p.lose_time)

            return self.total_players - finished.index(player)

        else:

            remains = sorted([player for player in self.players if player.lose_time is None], reverse=True,
                             key=lambda p: p.money + p.gived + p.in_pot)

            return remains.index(player) + 1

    def curr_standings(self, do_print_standings: bool) -> None:

        players = [player for table in self.tables for player in table.players.all_players()]
        there_is_controlled_player = any(player.controlled for player in players)

        self.average_stack = int(mean([player.money + player.gived + player.in_pot for player in players]))
        self.players_left = len(players)

        sorted_by_stack = sorted(players, key=lambda player: player.money + player.gived + player.in_pot, reverse=True)

        self.top_9 = sorted_by_stack[:9]

        if there_is_controlled_player and do_print_standings:
            Debug.standings(f'Average stack: {self.average_stack}')
            Debug.standings(f'Players left: {self.players_left}')
            Debug.standings(f'Top 10 stacks:')
            Debug.standings('\n'.join(f'{player.name} has {player.money}' for player in self.top_9))

            Debug.standings()
            Debug.standings('\n'.join(f'{player.name} has {player.money} and sits on '
                                      f'{sorted_by_stack.index(player) + 1}'
                                      for player in players if player.controlled))

    def infinite_resitting(self) -> None:

        while not self.game_finished and not self.game_broken:
            try:
                self.resit_players()

            except IndexError:
                Debug.resitting('Cannot resit - index error')

            else:
                sleep(0.01)

    def infinite(self) -> None:

        if self.online:

            self.blinds.start()

            self.resitting_thread = Thread(target=self.infinite_resitting, name='Resitting infinite')
            self.resitting_thread.start()

            counter = 0

            while not self.game_broken:

                if counter % 100 == 0:
                    Debug.game_progress(f'Tables = {len(self.tables)} '
                                        f'players = {sum(table.players.count for table in self.tables)}')

                self.curr_standings(counter % 100 == 0)

                for table in self.tables:
                    if not table.in_game and not table.wait:
                        table.run()

                if sum(table.players.count for table in self.tables) == 1:
                    Debug.game_progress('GAME OVER')
                    break

                counter += 1

                sleep(0.1)

        else:

            while not self.game_broken:

                if all(not table.in_game for table in self.tables):

                    self.resit_players()

                    for table in self.tables:
                        if table.players.count > 1:
                            self.do_one_hand()
                            break
                    else:
                        Debug.game_progress('GAME OVER')
                        break

                sleep(0.01)

        if not self.game_broken:

            if self.tables[0].online:
                self.tables[0].network.end()

            self.print_places()

        else:

            for table in self.tables:
                if table.online:

                    table.online = False
                    table.network.end()

                    for player in table.players.controlled:
                        player.network.socket.close()

                    for player in table.players.all_players():

                        if player.controlled:
                            del player.network

                        else:
                            player.play.busy = False

    def break_game(self) -> None:
        self.game_broken = True
