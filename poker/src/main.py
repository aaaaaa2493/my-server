from scipy.interpolate import splrep, splev
from matplotlib.pyplot import plot, show
from numpy import linspace
from re import compile
from datetime import datetime, timedelta
from calendar import month_name
from functools import lru_cache
from os import listdir, mkdir, makedirs, remove
from os.path import exists
from shutil import rmtree
from pickle import load, dump
from random import shuffle, random, choice, uniform, randint
from statistics import mean
from threading import Thread, Lock
from time import sleep
from typing import List, Dict, Tuple, Optional, Iterator, Union
from websocket import create_connection
from json import loads, dumps
from copy import deepcopy

from special.debug import Debug
from core.card import Card
from holdem.cards_pair import CardsPair
from holdem.holdem_poker import HoldemPoker as Poker, Hand
from core.deck import Deck
from learning.neural import Neural
from holdem.base_play import BasePlay
from special.settings import Settings, Mode




class Table:

    Tables = List['Table']

    class Delay:
        InitHand = 0
        Ante = 0.5
        CollectMoney = 1
        Blinds = 0.5
        BlindsIncreased = 0
        DealCards = 0.5
        DeletePlayer = 0
        AddPlayer = 0
        SwitchDecision = 0
        DummyMove = 1
        MadeDecision = 0.1
        ExcessMoney = 0.5
        Flop = 1
        Turn = 1
        River = 1
        OpenCards = 2
        GiveMoney = 2
        MoneyResults = 0
        HandResults = 0
        Clear = 0
        EndOfRound = 1

    class History:

        Decisions = List['Table.History.Decision']

        class Decision:

            def __init__(self, player: Player, decision: BasePlay.ResultType, money: int):

                self.player: Player = player
                self.decision: BasePlay.ResultType = decision
                self.money: int = money

            def __str__(self):
                return f'{self.player.cards} {self.player.id:>3} ' \
                       f'{BasePlay.Result.ToStr[self.decision]:<5} {self.money}'

        Steps = List['Table.History.Step']

        class Step:

            def __init__(self):

                self.decisions: Table.History.Decisions = []

            def add(self, player: Player, decision: BasePlay.ResultType, money: int) -> None:

                self.decisions += [Table.History.Decision(player, decision, money)]

        Hands = List['Table.History.Hands']

        class Hand:

            def __init__(self, number: int):

                self.number = number
                self.opened_cards: Card.Cards = None
                self.dealt_cards: List[Tuple[Player, CardsPair]] = None
                self.last_step: BasePlay.StepType = BasePlay.Step.Preflop

                self.preflop: Table.History.Step = Table.History.Step()
                self.flop: Table.History.Step = None
                self.turn: Table.History.Step = None
                self.river: Table.History.Step = None

            def add(self, player: Player, result: BasePlay.ResultType, money: int) -> None:

                if self.last_step == BasePlay.Step.River:
                    self.river.add(player, result, money)

                elif self.last_step == BasePlay.Step.Turn:
                    self.turn.add(player, result, money)

                elif self.last_step == BasePlay.Step.Flop:
                    self.flop.add(player, result, money)

                elif self.last_step == BasePlay.Step.Preflop:
                    self.preflop.add(player, result, money)

                else:
                    raise OverflowError('Undefined step')

            def give_cards(self, players: Players) -> None:

                self.dealt_cards = []

                for player in players.all_players():
                    self.dealt_cards += [(player, player.cards)]

            def next_step(self) -> None:

                if self.last_step == BasePlay.Step.Turn:
                    self.river = Table.History.Step()
                    self.last_step = BasePlay.Step.River

                elif self.last_step == BasePlay.Step.Flop:
                    self.turn = Table.History.Step()
                    self.last_step = BasePlay.Step.Turn

                elif self.last_step == BasePlay.Step.Preflop:
                    self.flop = Table.History.Step()
                    self.last_step = BasePlay.Step.Flop

                else:
                    raise OverflowError('Can not save more steps')

        def __init__(self, start_hand: int):

            self.number: int = start_hand
            self.curr: Table.History.Hand = Table.History.Hand(start_hand)
            self.hands: Table.History.Hands = []

        def save(self, cards: Card.Cards) -> None:

            self.curr.opened_cards = cards

            self.hands += [self.curr]
            self.number += 1
            self.curr = Table.History.Hand(self.number)

        def next_step(self) -> None:

            self.curr.next_step()

        def deal(self, players: Players) -> None:

            self.curr.give_cards(players)

        def add(self, player: Player, result: BasePlay.ResultType, money: int) -> None:

            self.curr.add(player, result, money)

    def __init__(self, game, _id: int, seats: int, blinds: Blinds, is_final: bool, start_hand: int = 1):

        self.game = game
        self.id: int = _id
        self.in_game = False
        self.wait: bool = False
        self.is_final: bool = is_final
        self.thread: Thread = None
        self.network: Network = None
        self.online: bool = False
        self.first_hand: bool = True
        self.raise_counter: int = 0
        self.lock = Lock()

        self.pot: Pot = Pot()
        self.deck: Deck = Deck()
        self.blinds: Blinds = blinds
        self.board: Board = Board(self.deck, start_hand)
        self.players: Players = Players(seats, _id, is_final)
        self.history: Table.History = Table.History(start_hand)

    def __del__(self):

        if self.online:
            del self.network

    def run(self):

        with self.lock:

            self.in_game = True
            self.thread = Thread(target=lambda: self.start_game(), name=f'Table {self.id}')

            if not self.wait:

                if Debug.Table and Debug.Decision and not self.online:
                    self.start_game()
                else:
                    self.thread.start()

    def save_history(self) -> None:

        for player in self.players.all_players():
            player.save_decisions()

        self.history.save(self.board.get())

    def collect_ante(self, ante: int) -> None:

        if self.blinds.ante > 0:

            all_paid = []
            for player in self.players.all_players():
                paid = player.pay_ante(ante)
                self.pot.money += paid
                all_paid += [(player, paid)]
                self.history.add(player, BasePlay.Result.Ante, paid)
                Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} paid ante {paid}')

            if self.online:
                self.network.ante(all_paid)
                sleep(Table.Delay.Ante)
                self.network.collect_money()
                sleep(Table.Delay.CollectMoney)

    def collect_blinds(self, sb: int, bb: int) -> None:

        self.players.to_button_seat()

        if self.players.count == 2:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            paid1 = player1.pay_blind(sb)
            self.history.add(player1, BasePlay.Result.SmallBlind, paid1)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player1.name} paid small blind {paid1}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(bb)
            self.history.add(player2, BasePlay.Result.BigBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid big blind {paid2}')

            if self.online:
                self.network.blinds(player1, [(player1, paid1), (player2, paid2)])
                sleep(Table.Delay.Blinds)

        elif self.players.game_without_small_blind and self.players.next_seat() is None:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(bb)
            self.history.add(player2, BasePlay.Result.BigBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid big blind {paid2}')

            if self.online:
                self.network.blinds(player1, [(player2, paid2)])
                sleep(Table.Delay.Blinds)

        else:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(sb)
            self.history.add(player2, BasePlay.Result.SmallBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid small blind {paid2}')
            player3 = self.players.next_player()
            paid3 = player3.pay_blind(bb)
            self.history.add(player3, BasePlay.Result.BigBlind, paid3)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player3.name} paid big blind {paid3}')

            if self.online:
                self.network.blinds(player1, [(player2, paid2), (player3, paid3)])
                sleep(Table.Delay.Blinds)

    def collect_pot(self) -> None:

        all_paid: int = 0

        for player in self.players.all_players():
            paid = player.move_money_to_pot()
            self.pot.money += paid
            all_paid += paid
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} paid to pot {paid}')
        Debug.table(f'Table {self.id} hand {self.board.hand}: total pot = {self.pot}')

        if all_paid > 0:

            if self.online:
                self.network.collect_money()
                sleep(Table.Delay.CollectMoney)

    def give_cards(self) -> None:

        for player in self.players.all_players():
            player.in_game = True

        self.deck.shuffle()

        button = self.players.to_button_seat()
        for _ in range(2):
            while button != self.players.next_busy_seat():
                self.players.get_curr_seat().add_card(self.deck.next())
            button.add_card(self.deck.next())

        self.history.deal(self.players)

        for player in self.players.controlled:
            self.network.give_cards(player)

        self.players.lock.release()

        if self.online:
            self.network.open_cards(self, True)
            sleep(Table.Delay.DealCards)

    def start_game(self) -> None:

        if self.wait:
            self.in_game = False
            return

        if self.players.count < 2:
            Debug.table(f'Table {self.id} has {self.players.count} player')
            self.in_game = False
            return

        for player in self.players.controlled:
            self.network.init_hand(player, self, self.game)
            player.network.place(self.game.find_place(player))

        if self.online:
            self.network.init_hand(None, self, self.game)
            sleep(Table.Delay.InitHand)

        if not self.first_hand:
            self.players.move_button()
        else:
            self.first_hand = False

        self.players.lock.acquire()

        ante = self.blinds.ante
        sb = self.blinds.small_blind
        bb = self.blinds.big_blind

        self.collect_ante(ante)

        for step in BasePlay.Step.GameSteps:

            if step == BasePlay.Step.Preflop:

                self.collect_blinds(sb, bb)

                self.give_cards()

                Debug.table(self)

                to_call = bb
                self.raise_counter = 1

            else:
                self.players.to_button()
                to_call = 0
                self.raise_counter = 0

            player = self.players.next_player()
            last_seat = player.id
            min_raise = bb
            can_raise_from = to_call + min_raise

            while True:

                if player.money > 0 and player.in_game and self.players.count_in_game_players() > 1 and not (
                            self.players.count_in_game_players() - self.players.count_all_in_players() == 1 and
                            max(p.gived for p in self.players.in_game_not_in_all_in_players()) >=
                            max(p.gived for p in self.players.all_in_players())):

                    if self.online:
                        self.network.switch_decision(player)
                        sleep(Table.Delay.SwitchDecision)

                    result = player.decide(step, to_call, can_raise_from, self.board.get(), self.online)

                    if self.online:
                        self.network.made_decision(player, result)
                        sleep(Table.Delay.MadeDecision)

                    player.history.set(step, result, self.raise_counter, player.in_all_in())
                    self.history.add(player, result, player.gived)

                    if result == BasePlay.Result.Raise or result == BasePlay.Result.Allin:

                        raised = player.gived
                        difference = raised - to_call

                        if difference > 0:
                            last_seat = player.id
                            to_call = raised
                        else:
                            Debug.error('ERROR IN DECISIONS')
                            raise ValueError('Error in decisions: player actually did not raised')

                        if difference >= min_raise:
                            min_raise = difference

                        self.raise_counter += 1
                        can_raise_from = raised + min_raise

                player = self.players.next_player()

                if last_seat == player.id:
                    break

            if self.online:
                sleep(Table.Delay.EndOfRound)

            if self.players.count_in_game_players() == 1:

                player_max_pot = max(p for p in self.players.in_game_players())
                second_max_pot = max(p.gived for p in self.players.all_players() if p != player_max_pot)
                difference = player_max_pot.gived - second_max_pot
                player_max_pot.gived -= difference
                player_max_pot.money += difference

                if self.online:
                    self.network.back_excess_money(player_max_pot, difference)
                    sleep(Table.Delay.ExcessMoney)

                self.history.add(player_max_pot, BasePlay.Result.ReturnMoney, difference)
                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'{difference} money back to {player_max_pot.name}')

                self.collect_pot()

                self.end_game()
                return

            if self.players.count_in_game_players() - self.players.count_all_in_players() <= 1:

                if self.players.count_in_game_players() == self.players.count_all_in_players():
                    max_all_in = sorted(p.gived + p.in_pot for p in self.players.all_players())[-2]
                    max_in_pot = max(p.gived + p.in_pot for p in self.players.in_game_players())

                else:
                    max_all_in = max([p.gived + p.in_pot for p in self.players.all_in_players()] +
                                     [p.gived + p.in_pot for p in self.players.not_in_game_players()])
                    max_in_pot = max(p.gived + p.in_pot for p in self.players.in_game_players())

                if max_in_pot > max_all_in:
                    player_max_pot = max(p for p in self.players.in_game_players()
                                         if p.gived + p.in_pot == max_in_pot)
                    difference = max_in_pot - max_all_in
                    player_max_pot.gived -= difference
                    player_max_pot.money += difference

                    if self.online:
                        self.network.back_excess_money(player_max_pot, difference)
                        sleep(Table.Delay.ExcessMoney)

                    self.history.add(player, BasePlay.Result.ReturnMoney, difference)
                    Debug.table(f'Table {self.id} hand {self.board.hand}: {difference} money back to {player.name}')

                self.collect_pot()

                if self.online:
                    self.network.open_cards(self)
                    sleep(Table.Delay.OpenCards)

                self.board.open_all_with_network(self)
                self.end_game()
                return

            if step == BasePlay.Step.Preflop:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open flop')
            elif step == BasePlay.Step.Flop:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open turn')
            elif step == BasePlay.Step.Turn:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open river')
            elif step == BasePlay.Step.River:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open cards')

                self.collect_pot()

                if self.online:
                    self.network.open_cards(self)
                    sleep(Table.Delay.OpenCards)

                self.end_game()
                return

            self.collect_pot()

            self.board.open_with_network(self)
            self.history.next_step()
            Debug.table(f'Table {self.id} hand {self.board.hand}: board {self.board}')

    def give_money(self, winner: Player) -> None:

        winner.in_pot = 0
        winner.money += winner.wins
        self.pot.money -= winner.wins

        self.history.add(winner, BasePlay.Result.WinMoney, winner.wins)

        if self.online:
            self.network.give_money(winner, winner.wins)
            sleep(Table.Delay.GiveMoney)

        winner.wins = 0
        winner.in_game = False

    def print_result(self) -> None:

        results = []

        for player in self.players.all_players():
            if player.money > player.money_last_time:

                results += [f'{player.name} wins {player.money - player.money_last_time}']

                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'player {player.name} wins {player.money - player.money_last_time} '
                            f'and has {player.money} money')
            elif player.money < player.money_last_time:

                results += [f'{player.name} loses {player.money_last_time - player.money}']

                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'player {player.name} loses {player.money_last_time - player.money} '
                            f'and has {player.money} money')
            else:
                Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} has {player.money} money')

        if self.online:
            self.network.money_results(results)
            sleep(Table.Delay.MoneyResults)

    def take_cards(self) -> None:

        for player in self.players.all_players():
            player.drop_cards()

        if self.online:
            self.network.clear()
            sleep(Table.Delay.Clear)

        self.board.clear()

    def end_game(self) -> None:

        Debug.table(f'Table {self.id} hand {self.board.hand}: cards - {self.board}')

        if self.players.count_in_game_players() == 1:

            if self.online:
                self.network.hand_results(self.board, [])
                sleep(Table.Delay.HandResults)

            winner = max(p for p in self.players.in_game_players())
            winner.wins += winner.in_pot

            winner.win_without_showdown(self.board.state)

            for player in self.players.all_players():
                if player != winner:
                    if winner.in_pot >= player.in_pot:
                        winner.wins += player.in_pot
                        player.in_pot = 0
                    else:
                        Debug.error('THERE IS SOME ERROR')

            self.give_money(winner)

        else:

            self.collect_pot()

            hand_results = []

            for player in self.players.in_game_players():

                player.hand = Poker.max_strength(player.cards.get() + self.board.get())

                hand_results += [(player.hand, player, str(player.hand))]

                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                            f'{player.get_cards()}, {player.name} has {player.hand}')
                player.play.goes_to_showdown += 1

            hand_results.sort(reverse=True, key=lambda x: x[0])

            if self.online:
                self.network.hand_results(self.board, hand_results)
                sleep(Table.Delay.HandResults)

            while self.players.count_in_game_players() > 0:

                wins_hand = max(player.hand for player in self.players.in_game_players())
                players_wins = [p for p in self.players.in_game_players() if p.hand == wins_hand]
                count_winners = len(players_wins)

                for player in players_wins:
                    player.play.wins_after_showdown += 1

                Debug.table(f"Table {self.id} hand {self.board.hand}: "
                            f"{', '.join(p.name for p in players_wins)} wins with {wins_hand}")

                all_inners = [p for p in self.players.all_in_players()]
                undivided_money = 0

                if len(all_inners) > 0:
                    all_inners_wins = sorted([p for p in all_inners if p in players_wins], key=lambda x: x.in_pot)

                    for player in all_inners_wins:

                        side_pot = player.in_pot
                        Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                    f'{player.name} opened pot with {player.in_pot}')

                        for opponent in self.players.all_players():
                            if opponent != player:
                                give_away = min(player.in_pot, opponent.in_pot)
                                Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                            f'{opponent.name} moved to pot {give_away}')
                                side_pot += give_away
                                opponent.in_pot -= give_away

                        win_for_everyone = side_pot / count_winners
                        if win_for_everyone % 1 != 0:
                            undivided_money = round((win_for_everyone % 1) * count_winners)

                        win_for_everyone = int(win_for_everyone)

                        if undivided_money > 0:

                            for lucky_man in self.players.sort_by_nearest_to_button(players_wins):
                                lucky_man.wins += 1
                                undivided_money -= 1

                                if undivided_money == 0:
                                    break

                        for winner in players_wins:
                            winner.wins += win_for_everyone
                            Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                        f'{winner.name} took {winner.wins} money from pot')

                        self.give_money(player)

                        del players_wins[players_wins.index(player)]
                        count_winners -= 1

                if count_winners > 0:

                    main_pot = sum(p.in_pot for p in players_wins)
                    Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                f'{" ".join(p.name for p in players_wins)} opened main pot with '
                                f'{main_pot // len(players_wins)} each and sum {main_pot}')

                    for player in self.players.all_players():
                        if player not in players_wins:
                            Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                        f'{player.name} move {player.in_pot} in main pot')
                            main_pot += player.in_pot
                            player.in_pot = 0
                            player.in_game = False

                    win_for_everyone = main_pot / count_winners
                    if win_for_everyone % 1 != 0:
                        undivided_money = round((win_for_everyone % 1) * count_winners)

                    win_for_everyone = int(win_for_everyone)

                    if undivided_money > 0:

                        for lucky_man in self.players.sort_by_nearest_to_button(players_wins):
                            lucky_man.wins += 1
                            undivided_money -= 1

                            if undivided_money == 0:
                                break

                    for winner in players_wins:
                        Debug.table(f'Table {self.id} hand {self.board.hand}: '
                                    f'{winner.name} took {win_for_everyone} money from main pot')
                        winner.wins += win_for_everyone
                        self.give_money(winner)

                for player in self.players.in_game_players():
                    if player.in_pot == 0:
                        player.in_game = False

        self.save_history()
        self.print_result()

        if self.pot.money != 0:
            Debug.error('ERROR IN POT')
            raise ValueError(f"POT != 0 pot = {self.pot.money}")

        self.players.remove_losers(self.game)
        self.take_cards()

        for player in self.players.all_players():
            if player.in_pot != 0:
                raise ValueError(f"POT != 0 on {player.name} POT = {player.in_pot}")

            if player.in_game:
                raise ValueError(f"{player.name} IN GAME AFTER ALL")

            if player.gived != 0:
                raise ValueError(f"GIVED != 0 on {player.name} gived = {player.gived}")

            if player.wins != 0:
                raise ValueError(f"WINS != 0 on {player.name} wins = {player.wins}")

        self.in_game = False

    def __str__(self):

        return f'Table {self.id} hand {self.board.hand}:\n{self.players}'


class Game:

    def __init__(self, players: int = 9, seats: int = 9, start_stack: int = 1000,
                 blinds: Blinds.SchemeType = Blinds.Scheme.Standard):

        if players < 1:
            raise ValueError("Can not be players less than one in new game")

        self.next_id: int = 0
        self.thread: Thread = None
        self.resitting_thread: Thread = None
        self.game_started: bool = False
        self.game_finished: bool = False
        self.game_broken: bool = False
        self.online: bool = False
        self.start_stack: int = start_stack
        self.total_players: int = players
        self.total_seats: int = seats
        self.total_tables: int = (players - 1) // seats + 1
        self.players_count: int = 0
        self.players: Players.TablePlayers = []
        self.blinds: Blinds = Blinds(blinds, self)

        if self.total_tables == 1:
            self.tables: Table.Tables = [Table(self, 0, seats, self.blinds, True)]
            self.final_table = self.tables[0]

        else:
            self.tables: Table.Tables = [Table(self, _id, seats, self.blinds, False)
                                         for _id in range(1, self.total_tables+1)]
            self.final_table = Table(self, 0, self.total_seats, self.blinds, True)

        self.average_stack: int = None
        self.players_left: int = None
        self.top_9: Players.TablePlayers = None

    def add_player(self, name: str = '') -> bool:

        if self.players_count == self.total_players:
            raise OverflowError(f'Player limit reached max = {self.total_players}')

        controlled = False
        if name:
            controlled = True

        player = Player(self.next_id, name, self.start_stack, controlled)
        self.next_id += 1

        self.players += [player]
        self.players_count += 1

        if self.players_count == self.total_players:
            self.thread = Thread(target=lambda: self.start_game(), name='Game infinite')
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

        if any(player.controlled for player in self.players):

            self.online = True
            Play.ExtendedName = False

            for table in self.tables:

                table.network = Network('tb', str(table.id))
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
            Debug.game_progress(f'Blinds are: {self.blinds.small_blind} {self.blinds.big_blind} {self.blinds.ante}')

        Debug.game_progress(f'Start hand {self.tables[0].board.hand} tables = {len(self.tables)} '
                            f'players = {sum(table.players.count for table in self.tables)}')

        for table in self.tables:
            table.run()

    def blinds_increased(self):

        Debug.game_progress(f'Blinds are: {self.blinds.small_blind} {self.blinds.big_blind} {self.blinds.ante}')

        sb = self.blinds.small_blind
        bb = self.blinds.big_blind
        ante = self.blinds.ante

        for table in self.tables:
            if table.online:
                table.network.blinds_increased(sb, bb, ante)
                sleep(Table.Delay.BlindsIncreased)

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
                    final_table.network = Network('tb', '0')
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

        for place, player in enumerate(sorted_players[:10]):
            Debug.evolution(f'{place+1:>4}) {player.play}')

        for place, player in enumerate(sorted_players):
            Debug.standings(f'{place+1:>4}) {player.name}')
            if not player.controlled:
                player.play.set_place(place+1, self.players_count)

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

            self.resitting_thread = Thread(target=lambda: self.infinite_resitting(), name='Resitting infinite')
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
                            player.network.socket.close()

                        else:
                            player.play.busy = False

    def break_game(self) -> None:
        self.game_broken = True


class Network:

    if Debug.Debug:
        ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'

    port = 9001

    def __init__(self, _id: str, name: str, is_dummy: bool = False, need_disconnect_info: bool = True):

        self.is_dummy = is_dummy
        self.need_disconnect_info = need_disconnect_info

        if not is_dummy:
            self.socket = create_connection(f'ws://{Network.ip}:{Network.port}')
            self.socket.send(f'{_id} {name}')

    def __del__(self):

        if not self.is_dummy:
            self.socket.close()

    def send(self, obj: dict) -> Optional[str]:

        if not self.is_dummy:
            if self.socket.connected:
                self.socket.send(dumps(obj))
        else:
            return dumps(obj)

    def send_raw(self, text: str) -> Optional[str]:

        if not self.is_dummy:
            if self.socket.connected:
                self.socket.send(text)
        else:
            return text

    def receive(self) -> dict:

        if self.socket.connected and not self.is_dummy:
            return loads(self.socket.recv())

    def receive_raw(self) -> str:

        if self.socket.connected and not self.is_dummy:
            return self.socket.recv()

    def input_decision(self, available) -> Optional[List[str]]:

        if self.is_dummy:
            return

        to_send = dict()

        to_send['type'] = 'set decision'

        decisions = list()

        for decision in available:

            curr = dict()

            if decision[0] == BasePlay.Result.Fold:
                curr['type'] = 'fold'

            elif decision[0] == BasePlay.Result.Check:
                curr['type'] = 'check'

            elif decision[0] == BasePlay.Result.Call:
                curr['type'] = 'call'
                curr['money'] = decision[1]

            elif decision[0] == BasePlay.Result.Raise:
                curr['type'] = 'raise'
                curr['from'] = decision[1]
                curr['to'] = decision[2]

            elif decision[0] == BasePlay.Result.Allin:
                curr['type'] = 'all in'
                curr['money'] = decision[1]

            else:
                raise ValueError(f'THERE IS ANOTHER DECISION {decision[0]}')

            decisions += [curr]

        to_send['decisions'] = decisions

        self.send_raw(f'decision {dumps(to_send)}')

        reply = self.receive_raw()

        if reply is None:
            reply = '1'

        return reply.split()

    def init_hand(self, player: Optional[Player], table: Table, game: Game) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'init hand'
        to_send['table_number'] = table.id
        to_send['seats'] = table.players.total_seats
        to_send['hand_number'] = table.board.hand
        to_send['ante'] = table.blinds.ante
        to_send['sb'] = table.blinds.small_blind
        to_send['bb'] = table.blinds.big_blind
        to_send['avg_stack'] = game.average_stack
        to_send['players_left'] = game.players_left
        to_send['is_final'] = table.is_final

        top_9 = list()

        for curr_player in game.top_9:
            curr = dict()
            curr['name'] = curr_player.name
            curr['stack'] = curr_player.money + curr_player.gived + curr_player.in_pot
            top_9 += [curr]

        to_send['top_9'] = top_9

        players = list()

        if player is not None:

            for curr_player in table.players.players:
                curr = dict()

                if curr_player is None:
                    curr['id'] = None

                else:
                    curr['id'] = curr_player.id
                    curr['name'] = curr_player.name
                    curr['stack'] = curr_player.money
                    curr['controlled'] = player is curr_player

                players += [curr]

        else:

            for curr_player in table.players.players:
                curr = dict()

                if curr_player is None:
                    curr['id'] = None

                else:
                    curr['id'] = curr_player.id
                    curr['name'] = curr_player.name
                    curr['stack'] = curr_player.money
                    curr['controlled'] = True

                players += [curr]

        to_send['players'] = players

        if self.need_disconnect_info:
            return self.send_raw(f'{"new_hand" if player is None else f"player_hand {player.id} "} {dumps(to_send)}')
        else:
            return self.send(to_send)

    def ante(self, all_paid: List[Tuple[Player, int]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'ante'

        paid_send = list()

        for player, paid in all_paid:
            curr = dict()
            curr['id'] = player.id
            curr['paid'] = paid
            paid_send += [curr]

        to_send['paid'] = paid_send

        return self.send(to_send)

    def collect_money(self) -> Optional[str]:

        return self.send({'type': 'collect money'})

    def blinds(self, button: Player, blind_info: List[Tuple[Player, int]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'blinds'
        to_send['button'] = button.id

        blind_send = list()

        for curr_blind, paid in blind_info:
            curr = dict()
            curr['id'] = curr_blind.id
            curr['paid'] = paid
            blind_send += [curr]

        to_send['info'] = blind_send

        return self.send(to_send)

    def blinds_increased(self, sb: int, bb: int, ante: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'blinds increased'
        to_send['sb'] = sb
        to_send['bb'] = bb
        to_send['ante'] = ante

        return self.send(to_send)

    def give_cards(self, player: Player) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'give cards'
        to_send['first'] = player.cards.first.card
        to_send['second'] = player.cards.second.card

        return self.send_raw(f'give_cards {player.id} {dumps(to_send)}')

    def deal_cards(self) -> Optional[str]:

        return self.send({'type': 'deal cards'})

    def delete_player(self, player: Player) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'delete player'
        to_send['id'] = player.id

        return self.send(to_send)

    def add_player(self, player: Player, seat: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'add player'
        to_send['name'] = player.name
        to_send['id'] = player.id
        to_send['stack'] = player.money
        to_send['seat'] = seat

        if self.need_disconnect_info:
            return self.send_raw(f'add_player {dumps(to_send)}')
        else:
            return self.send(to_send)

    def resit(self, player: Player, players: Players) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'resit'
        to_send['table_number'] = players.id
        to_send['is_final'] = players.is_final
        to_send['seats'] = players.total_seats

        players_send = list()

        for curr_player in players.players:
            curr = dict()

            if curr_player is None:
                curr['id'] = None

            else:
                curr['id'] = curr_player.id
                curr['name'] = curr_player.name
                curr['stack'] = curr_player.money
                curr['controlled'] = player is curr_player

            players_send += [curr]

        to_send['players'] = players_send

        if self.need_disconnect_info:
            return self.send_raw(f'resit {players.id} {dumps(to_send)}')
        else:
            return self.send(to_send)

    def switch_decision(self, player: Player) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'switch decision'
        to_send['id'] = player.id

        return self.send(to_send)

    def made_decision(self, player: Player, decision: BasePlay.ResultType) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'made decision'

        if decision == BasePlay.Result.Fold:
            to_send['result'] = 'fold'

        elif decision == BasePlay.Result.Check:
            to_send['result'] = 'check'

        elif decision == BasePlay.Result.Call:
            to_send['result'] = 'call'
            to_send['money'] = player.gived

        elif decision == BasePlay.Result.Raise:
            to_send['result'] = 'raise'
            to_send['money'] = player.gived

        elif decision == BasePlay.Result.Allin:
            to_send['result'] = 'all in'
            to_send['money'] = player.gived

        else:
            raise ValueError(f'I FORGOT ABOUT RESULT ID {decision}')

        return self.send(to_send)

    def back_excess_money(self, player: Player, money: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'excess money'
        to_send['id'] = player.id
        to_send['money'] = money

        return self.send(to_send)

    def flop(self, card1: Card, card2: Card, card3: Card) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'flop'
        to_send['card1'] = card1.card
        to_send['card2'] = card2.card
        to_send['card3'] = card3.card

        return self.send(to_send)

    def turn(self, card: Card) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'turn'
        to_send['card'] = card.card

        return self.send(to_send)

    def river(self, card: Card) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'river'
        to_send['card'] = card.card

        return self.send(to_send)

    def open_cards(self, table: Table, for_replay=False) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'open cards'

        cards = list()

        for player in table.players.in_game_players():
            curr = dict()
            curr['id'] = player.id

            if player.cards is None:
                curr['card1'] = Card.UndefinedCard
                curr['card2'] = Card.UndefinedCard

            else:

                if player.cards.first is not None:
                    curr['card1'] = player.cards.first.card
                else:
                    curr['card1'] = Card.UndefinedCard

                if player.cards.second is not None:
                    curr['card2'] = player.cards.second.card
                else:
                    curr['card2'] = Card.UndefinedCard

            cards += [curr]

        to_send['cards'] = cards

        if for_replay:
            return self.send_raw(f'for_replay {dumps(to_send)}')

        else:
            return self.send(to_send)

    def give_money(self, player: Player, money: int) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'give money'
        to_send['id'] = player.id
        to_send['money'] = money

        return self.send(to_send)

    def money_results(self, results: List[str]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'money results'
        to_send['results'] = results

        return self.send(to_send)

    def hand_results(self, board: Board, results: List[Tuple[Hand, Player, str]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'hand results'

        if board.state == BasePlay.Step.Preflop:
            to_send['flop1'] = Card.UndefinedCard
            to_send['flop2'] = Card.UndefinedCard
            to_send['flop3'] = Card.UndefinedCard
            to_send['turn'] = Card.UndefinedCard
            to_send['river'] = Card.UndefinedCard

        elif board.state == BasePlay.Step.Flop:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = Card.UndefinedCard
            to_send['river'] = Card.UndefinedCard

        elif board.state == BasePlay.Step.Turn:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = board.turn.card
            to_send['river'] = Card.UndefinedCard

        elif board.state == BasePlay.Step.River:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = board.turn.card
            to_send['river'] = board.river.card

        else:
            raise OverflowError('Undefined board state')

        results_send = list()

        for hand, player, result in results:

            curr = dict()
            curr['id'] = player.id
            curr['name'] = player.name

            if player.cards.first is None:
                curr['first'] = Card.UndefinedCard
            else:
                curr['first'] = player.cards.first.card

            if player.cards.second is None:
                curr['second'] = Card.UndefinedCard
            else:
                curr['second'] = player.cards.second.card

            for i in range(5):
                if hand.cards[i] is None:
                    curr[f'card{i+1}'] = Card.UndefinedCard
                else:
                    curr[f'card{i+1}'] = hand.cards[i].card

            curr['result'] = result

            results_send += [curr]

        to_send['results'] = results_send

        return self.send(to_send)

    def busted(self, place: int) -> None:

        if not self.is_dummy:
            self.send_raw('busted')
            self.send({'type': 'busted', 'place': place})
            self.socket.close()

    def clear(self) -> Optional[str]:

        return self.send({'type': 'clear'})

    def win(self) -> None:

        if not self.is_dummy:
            self.send({'type': 'win'})
            self.socket.close()

    def place(self, place: int) -> Optional[str]:

        return self.send({'type': 'place', 'place': place})

    def end(self) -> Optional[str]:

        return self.send_raw('end')


class PokerGame:

    path_to_raw_games = 'games/raw/'
    path_to_parsed_games = 'games/parsed/'
    path_to_converted_games = 'games/converted/'

    EventType = int

    class Event:
        Fold = 0
        Call = 1
        Check = 2
        Raise = 3
        Allin = 4
        Ante = 5
        SmallBlind = 6
        BigBlind = 7
        WinMoney = 8
        ReturnMoney = 9
        ChatMessage = 10
        ObserverChatMessage = 11
        Disconnected = 12
        Connected = 13
        FinishGame = 14

        ToResult = {Fold: BasePlay.Result.Fold,
                    Check: BasePlay.Result.Check,
                    Call: BasePlay.Result.Call,
                    Raise: BasePlay.Result.Raise,
                    Allin: BasePlay.Result.Allin}

        ToStr = {Fold: 'fold',
                 Call: 'call',
                 Check: 'check',
                 Raise: 'raise',
                 Allin: 'all in',
                 Ante: 'ante',
                 SmallBlind: 'sb',
                 BigBlind: 'bb',
                 WinMoney: 'win',
                 ReturnMoney: 'return',
                 ChatMessage: 'chat message',
                 ObserverChatMessage: 'observer message',
                 Disconnected: 'disconnected',
                 Connected: 'connected',
                 FinishGame: 'finished'}

    class MockPlayer:

        class PlayerEvent:

            def __init__(self, event: 'PokerGame.EventType', money: int):
                self.event: PokerGame.EventType = event
                self.money: int = money

        def __init__(self, name: str, money: int, seat: int, is_active: bool):
            self.name: str = name
            self.money: int = money
            self.seat: int = seat
            self.is_active = is_active
            self.is_all_in: bool = False
            self.is_winner: bool = False
            self.is_loser: bool = False
            self.cards: CardsPair = None
            self.preflop: List['PokerGame.MockPlayer.PlayerEvent'] = []
            self.flop: List['PokerGame.MockPlayer.PlayerEvent'] = []
            self.turn: List['PokerGame.MockPlayer.PlayerEvent'] = []
            self.river: List['PokerGame.MockPlayer.PlayerEvent'] = []

        def get_list(self, step: BasePlay.StepType) -> List['PokerGame.MockPlayer.PlayerEvent']:

            if step == BasePlay.Step.Preflop:
                return self.preflop
            elif step == BasePlay.Step.Flop:
                return self.flop
            elif step == BasePlay.Step.Turn:
                return self.turn
            elif step == BasePlay.Step.River:
                return self.river
            else:
                raise ValueError('No such step id ' + str(step))

        def add_decision(self, step: BasePlay.StepType, event: 'PokerGame.EventType', money: int) -> None:
            self.get_list(step).append(PokerGame.MockPlayer.PlayerEvent(event, money))

        def gived(self, step: BasePlay.StepType) -> int:

            curr_list = self.get_list(step)
            for action in reversed(curr_list):

                if action.event == PokerGame.Event.Check:
                    return 0

                elif action.event == PokerGame.Event.Allin or \
                        action.event == PokerGame.Event.BigBlind or \
                        action.event == PokerGame.Event.SmallBlind or \
                        action.event == PokerGame.Event.Call or \
                        action.event == PokerGame.Event.Raise:
                    return action.money

            return 0

    class ObserverPlayer:
        def __init__(self, name):
            self.name = name

    class PokerEvent:

        def __init__(self, player: Union['PokerGame.MockPlayer', 'PokerGame.ObserverPlayer'],
                     event: 'PokerGame.EventType', money: int, msg: str):
            self.player = player
            self.event: PokerGame.EventType = event
            self.money: int = money
            self.message: str = msg

        def __str__(self) -> str:
            if self.event == PokerGame.Event.Fold or \
                    self.event == PokerGame.Event.Check or \
                    self.event == PokerGame.Event.Disconnected or \
                    self.event == PokerGame.Event.Connected:
                return f'{self.player.name} {PokerGame.Event.ToStr[self.event]}'

            elif self.event == PokerGame.Event.Call or \
                    self.event == PokerGame.Event.Raise or \
                    self.event == PokerGame.Event.Allin or \
                    self.event == PokerGame.Event.Ante or \
                    self.event == PokerGame.Event.SmallBlind or \
                    self.event == PokerGame.Event.BigBlind or \
                    self.event == PokerGame.Event.WinMoney or \
                    self.event == PokerGame.Event.ReturnMoney:
                return f'{self.player.name} {PokerGame.Event.ToStr[self.event]} {self.money}'

            elif self.event == PokerGame.Event.ChatMessage:
                return f'{self.player.name}: {self.message}'

            elif self.event == PokerGame.Event.ObserverChatMessage:
                return f'{self.player.name} [observer]: {self.message}'

            elif self.event == PokerGame.Event.FinishGame:
                return f'{self.player.name} {PokerGame.Event.ToStr[self.event]} ' \
                       f'{self.message} and get {self.money / 100}'

            raise ValueError(f'Do not know how to interpret Event id {self.event}')

    class PokerHand:

        def __init__(self, players: List['PokerGame.MockPlayer']):
            self.id: int = 0
            self.players: List[PokerGame.MockPlayer] = players
            self.sit_during_game: List[PokerGame.MockPlayer] = None
            self.preflop: List[PokerGame.PokerEvent] = []
            self.flop: List[PokerGame.PokerEvent] = []
            self.turn: List[PokerGame.PokerEvent] = []
            self.river: List[PokerGame.PokerEvent] = []
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
            self.curr_step: BasePlay.StepType = BasePlay.Step.Preflop
            self.curr_events: List[PokerGame.PokerEvent] = self.preflop

        def init(self, hand_id, sb, bb, out_of_hand, table_num, button):
            self.id = hand_id
            self.small_blind = sb
            self.big_blind = bb
            self.sit_during_game = out_of_hand
            self.table_id = table_num
            self.button_seat = button

        def add_winner(self, name: str) -> None:
            self.get_player(name).is_winner = True

        def get_winners(self) -> List['PokerGame.MockPlayer']:
            return [player for player in self.players if player.is_winner]

        def get_losers(self) -> List['PokerGame.MockPlayer']:
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

        def get_player(self, name: str) -> 'PokerGame.MockPlayer':
            return max(player for player in self.players if player.name == name)

        def add_decision(self, name: str, event: 'PokerGame.EventType', money: int, msg: str = '') -> None:
            if event == PokerGame.Event.ObserverChatMessage:
                self.curr_events += [PokerGame.PokerEvent(PokerGame.ObserverPlayer(name), event, money, msg)]
            else:
                player = self.get_player(name)
                self.curr_events += [PokerGame.PokerEvent(player, event, money, msg)]
                player.add_decision(self.curr_step, event, money)

        def set_all_in(self, name: str) -> None:
            self.get_player(name).is_all_in = True

        def get_only_all_in(self) -> str:
            return max(player for player in self.players if player.is_all_in).name

        def switch_to_step(self, step: BasePlay.StepType) -> None:

            self.curr_step = step

            if step == BasePlay.Step.Preflop:
                self.curr_events = self.preflop
            elif step == BasePlay.Step.Flop:
                self.curr_events = self.flop
            elif step == BasePlay.Step.Turn:
                self.curr_events = self.turn
            elif step == BasePlay.Step.River:
                self.curr_events = self.river
            else:
                raise ValueError('No such step id ' + str(step))

        def next_step(self) -> None:
            self.switch_to_step(BasePlay.Step.next_step(self.curr_step))

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

    def __init__(self):
        self.id: int = 0
        self.name: str = ''
        self.date: str = ''
        self.time: str = ''
        self.source: str = ''
        self.seats: int = 0
        self.hands: List[PokerGame.PokerHand] = []
        self.curr_hand: PokerGame.PokerHand = None

    def init(self, id_, name, seats, date, time):
        self.id = id_
        self.name = name
        self.seats = seats
        self.date = date
        self.time = time

    def add_hand(self, players: List['PokerGame.MockPlayer']):
        new_hand = PokerGame.PokerHand(players)
        self.hands += [new_hand]
        self.curr_hand = new_hand

    def save(self, path: str = '') -> None:

        if path == '':
            path = self.source

        if not exists('games'):
            mkdir('games')

        if not exists('games/parsed'):
            mkdir('games/parsed')

        path = PokerGame.path_to_parsed_games + path
        *dirs, file_name = path.split('/')

        dirs = '/'.join(dirs)

        if not exists(dirs):
            makedirs(dirs)

        dump(self, open(path, 'wb'))

    @staticmethod
    def load(path: str) -> 'PokerGame':
        return load(open(PokerGame.path_to_parsed_games + path, 'rb'))

    def convert(self) -> None:

        if not exists('games'):
            mkdir('games')

        if not exists('games/converted'):
            mkdir('games/converted')
            
        current_date = datetime.now()
            
        if self.date == '' or self.time == '':
            date = current_date.strftime('%Y/%m/%d')
            time = current_date.strftime('%H:%M:%S')
        else:
            date = self.date
            time = self.time

        year, month, day = date.split('/')

        if len(month) == 1:
            month = '0' + month
        if len(day) == 1:
            day = '0' + day

        hour, minute, second = time.split(':')

        if len(hour) == 1:
            hour = '0' + hour
        if len(minute) == 1:
            minute = '0' + minute
        if len(second) == 1:
            second = '0' + second

        folder_name = f'{year}-{month}-{day}_{hour}-{minute}-{second} 1 {self.seats} {len(self.hands)} {self.name}'

        path = PokerGame.path_to_converted_games + 'games/' + folder_name
        chat_path = PokerGame.path_to_converted_games + 'chat/' + folder_name

        if exists(path):
            rmtree(path)

        if exists(chat_path):
            rmtree(chat_path)

        table_folder = f'/0 {len(self.hands)}'

        path += table_folder

        makedirs(path)
        makedirs(chat_path)

        time = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), 0)
        network = Network('', '', True, False)
        chat_messages: List[Tuple[datetime, str]] = []

        for num, hand in enumerate(self.hands):

            converted: List[Tuple[datetime, str]] = []
            hand.switch_to_step(BasePlay.Step.Preflop)
            events: Iterator[PokerGame.PokerEvent] = iter(hand.curr_events)

            game = Game(self.seats, self.seats, 0)
            table = game.final_table
            table.is_final = hand.is_final

            table.id = hand.table_id
            table.players.total_seats = self.seats
            table.board.hand = num + 1
            table.blinds.ante = hand.ante
            table.blinds.small_blind = hand.small_blind
            table.blinds.big_blind = hand.big_blind

            game.average_stack = int(mean(player.money for player in hand.players))
            game.players_left = hand.players_left

            players: List[Player] = []
            find: Dict[int, Player] = dict()

            for seat in range(1, self.seats + 1):

                player = sorted(player for player in hand.players if player.seat == seat)
                if not player:
                    player = None
                elif len(player) == 1:
                    player = player[0]
                else:
                    raise ValueError('Two players with same seat')

                if player is not None:
                    new_player = Player(player.seat, player.name, player.money, True, True)
                    new_player.in_game = True
                    new_player.cards = player.cards
                    players += [new_player]
                    find[player.seat] = new_player
                else:
                    players += [None]

            game.top_9 = sorted([p for p in players if p is not None], key=lambda p: p.money, reverse=True)
            table.players.players = players

            json_message = loads(network.init_hand(None, table, game))
            for curr in json_message['players']:
                if curr['id'] is not None:
                    pl = max(pl for pl in hand.players if pl.seat == curr['id'])
                    curr['disconnected'] = not pl.is_active
                else:
                    curr['disconnected'] = False
            init_message = dumps(json_message)

            converted += [(time, init_message)]
            time = time + timedelta(seconds=Table.Delay.InitHand)

            converted += [(time, network.deal_cards())]
            time = time + timedelta(seconds=0)

            converted += [(time, network.open_cards(table))]
            time = time + timedelta(seconds=Table.Delay.DealCards)

            event = next(events)

            if hand.ante > 0:

                paid: List[Tuple[Player, int]] = []
                while event.event == PokerGame.Event.Ante:
                    paid += [(find[event.player.seat], event.money)]
                    event = next(events)

                converted += [(time, network.ante(paid))]
                time = time + timedelta(seconds=Table.Delay.Ante)

                converted += [(time, network.collect_money())]
                time = time + timedelta(seconds=Table.Delay.CollectMoney)

            button: Player = find[hand.button_seat]

            blinds_info: List[Tuple[Player, int]] = []

            if event.event == PokerGame.Event.SmallBlind:
                blinds_info += [(find[event.player.seat], event.money)]
                event = next(events)

            if event.event == PokerGame.Event.BigBlind:
                blinds_info += [(find[event.player.seat], event.money)]
                event = next(events)

            converted += [(time, network.blinds(button, blinds_info))]
            time = time + timedelta(seconds=Table.Delay.Blinds)

            if hand.sit_during_game:

                for player in hand.sit_during_game:
                    converted += [(time, network.add_player(Player(player.seat, player.name,
                                                                   player.money, True, True), player.seat - 1))]
                    time = time + timedelta(seconds=Table.Delay.AddPlayer)

            avoid_in_first_iteration = True
            need_to_collect_money = True

            while True:

                if hand.curr_step == BasePlay.Step.River:
                    break

                elif not avoid_in_first_iteration:

                    hand.next_step()

                    need_to_continue = False

                    if hand.curr_step == BasePlay.Step.Flop and \
                            hand.board.flop1 is not None and \
                            hand.board.flop2 is not None and \
                            hand.board.flop3 is not None:
                        converted += [(time, network.flop(hand.board.flop1, hand.board.flop2, hand.board.flop3))]
                        time = time + timedelta(seconds=Table.Delay.Flop)
                        need_to_continue = True

                    elif hand.curr_step == BasePlay.Step.Turn and hand.board.turn is not None:
                        converted += [(time, network.turn(hand.board.turn))]
                        time = time + timedelta(seconds=Table.Delay.Turn)
                        need_to_continue = True

                    elif hand.curr_step == BasePlay.Step.River and hand.board.river is not None:
                        converted += [(time, network.river(hand.board.river))]
                        time = time + timedelta(seconds=Table.Delay.River)
                        need_to_continue = True

                    events = iter(hand.curr_events)

                    try:
                        event = next(events)
                    except StopIteration:
                        if need_to_continue:
                            continue
                        else:
                            break

                else:
                    avoid_in_first_iteration = False

                while True:

                    if event.event == PokerGame.Event.Fold or \
                            event.event == PokerGame.Event.Check or \
                            event.event == PokerGame.Event.Call or \
                            event.event == PokerGame.Event.Raise or \
                            event.event == PokerGame.Event.Allin:

                        if event.event == PokerGame.Event.Call or \
                                event.event == PokerGame.Event.Raise or \
                                event.event == PokerGame.Event.Allin:
                            need_to_collect_money = True

                        player = find[event.player.seat]
                        player.gived = event.money

                        converted += [(time, network.switch_decision(player))]
                        time = time + timedelta(seconds=Table.Delay.SwitchDecision + Table.Delay.DummyMove)

                        converted += [(time, network.made_decision(player, PokerGame.Event.ToResult[event.event]))]
                        time = time + timedelta(seconds=Table.Delay.MadeDecision)

                    elif event.event == PokerGame.Event.WinMoney:

                        if need_to_collect_money:
                            converted += [(time, network.collect_money())]
                            time = time + timedelta(seconds=Table.Delay.CollectMoney)
                            need_to_collect_money = False

                        converted += [(time, network.give_money(find[event.player.seat], event.money))]
                        time = time + timedelta(seconds=Table.Delay.GiveMoney)

                    elif event.event == PokerGame.Event.ReturnMoney:

                        if sum(e.event == PokerGame.Event.Allin or
                               e.event == PokerGame.Event.Raise or
                               e.event == PokerGame.Event.Call or
                               e.event == PokerGame.Event.SmallBlind or
                               e.event == PokerGame.Event.BigBlind for e in hand.curr_events) == 1:
                            need_to_collect_money = False

                        converted += [(time, network.back_excess_money(find[event.player.seat], event.money))]
                        time = time + timedelta(seconds=Table.Delay.ExcessMoney)

                    elif event.event == PokerGame.Event.ChatMessage:

                        chat_message = network.send({'type': 'chat', 'text': f'{event.player.name}: {event.message}'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == PokerGame.Event.ObserverChatMessage:

                        chat_message = network.send({'type': 'chat',
                                                     'text': f'{event.player.name} [observer]: {event.message}'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == PokerGame.Event.Disconnected:

                        converted += [(time, network.send({'type': 'disconnected', 'id': event.player.seat}))]
                        time = time + timedelta(seconds=0)

                        chat_message = network.send({'type': 'chat', 'text': f'{event.player.name} disconnected'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == PokerGame.Event.Connected:

                        converted += [(time, network.send({'type': 'connected', 'id': event.player.seat}))]
                        time = time + timedelta(seconds=0)

                        chat_message = network.send({'type': 'chat', 'text': f'{event.player.name} connected'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == PokerGame.Event.FinishGame:

                        if event.money == 0:
                            chat_message = network.send({'type': 'chat',
                                                         'text': f'{event.player.name} finished {event.message}'})

                        else:
                            chat_message = network.send({'type': 'chat',
                                                         'text': f'{event.player.name} '
                                                                 f'finished {event.message} and get '
                                                                 f'${event.money // 100}.{event.money % 100}'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                        if event.message != '1st':
                            converted += [(time, network.delete_player(find[event.player.seat]))]
                            time = time + timedelta(seconds=Table.Delay.DeletePlayer)

                    else:
                        raise ValueError(f'Undefined event id {event.event}')

                    try:
                        event = next(events)
                    except StopIteration:

                        time = time + timedelta(seconds=Table.Delay.EndOfRound)

                        if need_to_collect_money:

                            converted += [(time, network.collect_money())]
                            time = time + timedelta(seconds=Table.Delay.CollectMoney)
                            need_to_collect_money = False

                        break

            results: List[Tuple[Hand, Player, str]] = []

            for player in hand.players:
                if player.cards is not None:
                    if hand.board.state == BasePlay.Step.Preflop:
                        if not player.cards.initialized():
                            curr_hand = Poker.strength1(player.cards.first)
                        else:
                            curr_hand = Poker.strength2(player.cards.first, player.cards.second)

                    elif hand.board.state == BasePlay.Step.Flop:
                        if not player.cards.initialized():
                            curr_hand = Poker.strength4(player.cards.first, hand.board.flop1,
                                                        hand.board.flop2, hand.board.flop3)
                        else:
                            curr_hand = Poker.strength(player.cards.first, player.cards.second,
                                                       hand.board.flop1, hand.board.flop2, hand.board.flop3)

                    else:
                        cards = hand.board.get()

                        if not player.cards.initialized():
                            cards += [player.cards.first]
                        else:
                            cards += [player.cards.first, player.cards.second]

                        curr_hand = Poker.max_strength(cards)

                    results += [(curr_hand, find[player.seat], '')]

            results.sort(reverse=True, key=lambda x: x[0])

            converted += [(time, network.hand_results(hand.board, results))]
            time = time + timedelta(seconds=Table.Delay.HandResults)

            converted += [(time, network.clear())]
            time = time + timedelta(seconds=Table.Delay.Clear)

            output = ''

            for d, s in converted:
                output += '%s %s %s %s %s %s %s' % (d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond)
                output += '\n'
                output += s
                output += '\n'

            open(path + '/%s' % (num,), 'w').write(output)

        chat_output = ''

        for d, s in chat_messages:
            chat_output += '%s %s %s %s %s %s %s' % (d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond)
            chat_output += '\n'
            chat_output += s
            chat_output += '\n'

        open(chat_path + table_folder, 'w').write(chat_output)

    def approximate_players_left(self):

        good_hands = [(self.hands.index(hand), hand) for hand in self.hands if hand.players_left > 0]

        if len(good_hands) == 0:
            return

        if len(good_hands) == 1:
            only_info = good_hands[0][1].players_left
            for hand in self.hands:
                hand.players_left = only_info
            return

        if self.hands[0].players_left == 0:
            players_difference = good_hands[0][1].players_left - good_hands[1][1].players_left
            hands_difference = good_hands[1][0] - good_hands[0][0]
            players_per_hand = players_difference / hands_difference
            for count, index in enumerate(range(good_hands[0][0] - 1, -1, -1)):
                self.hands[index].players_left = good_hands[0][1].players_left + int((count + 1) * players_per_hand)

        for (from_index, from_hand), (to_index, to_hand) in zip(good_hands, good_hands[1:]):
            players_difference = from_hand.players_left - to_hand.players_left
            hands_difference = to_index - from_index
            players_per_hand = players_difference / hands_difference
            for count, hand_index in enumerate(range(from_index + 1, to_index)):
                self.hands[hand_index].players_left = from_hand.players_left - int((count + 1) * players_per_hand) - 1

    def add_final_table_marks(self):
        for hand in self.hands:
            if hand.players_left == len(hand.players) + len(hand.sit_during_game):
                hand.is_final = True

    def __str__(self) -> str:
        ret = [f'Poker game of {len(self.hands)} hands']
        i: int = 1
        for hand in self.hands:
            ret += [f'Hand #{i}']
            ret += [str(hand)]
            i += 1
        return '\n'.join(ret)


class NeuralNetwork:

    class PokerDecision:

        class Bubble:

            # coefficients for y = ax**2 + bx + c
            A_COEFFICIENT = 1501 / 1764
            B_COEFFICIENT = 10375 / 588
            C_COEFFICIENT = - 8375 / 882

            def __init__(self, total_players: int, total_prizes: int):

                a = self.A_COEFFICIENT
                b = self.B_COEFFICIENT
                c = self.C_COEFFICIENT - total_players

                self.total_prizes = total_prizes
                self.total_players = total_players

                self.bubble_count = round((-b + (b*b - 4*a*c)**.5) / (2*a))

                x_points = [total_prizes - 1,
                            total_prizes,
                            total_prizes + 1,
                            total_prizes + self.bubble_count + 1,
                            total_prizes + 2 * self.bubble_count + 1,
                            total_prizes + 3 * self.bubble_count + 1,
                            total_prizes + 4 * self.bubble_count + 1,
                            total_prizes + 5 * self.bubble_count + 1,
                            total_prizes + 6 * self.bubble_count + 1,
                            total_prizes + 7 * self.bubble_count + 1,
                            total_players + 7 * self.bubble_count + 1,
                            total_players + 7 * self.bubble_count + 2,
                            total_players + 7 * self.bubble_count + 3]

                y_points = [1, 1, 1, 0.8, 0.2, 0.02, 0.002, 0, 0, 0, 0, 0, 0]

                self.spline = splrep(x_points, y_points)

            def get(self, point: float) -> float:
                if point < self.total_prizes + 1 or point > self.total_players:
                    return 0
                return float(splev([point], self.spline))

            def show(self, points: int = 10000):
                x_coords = linspace(0, self.total_players, points)
                y_coords = [self.get(i) for i in x_coords]
                plot(x_coords, y_coords)
                show()


class GameParser:

    class RegEx:

        class PokerStars:
            name = '[a-zA-Z0-9_\-@\'.,$*`áàåäãçéèêíîóöôõšüúžÄÁÃÅÉÍÖÔÓÜØø´<^>+&' \
                   '\\\/()Ð€£¼ñ®™~#!%\[\]|°¿?:"=ß{}æ©«»¯²¡; ]+'

            identifier = compile(r'^[*\n#1 ]*PokerStars Hand #')

            hand_border = compile(r'[*]{11} # [0-9]+ [*]{14}')
            hand_border_2 = compile('\n\n\n\n')
            step_border = compile(r'[*]{3} [A-Z ]+ [*]{3}')
            hand_and_game_id = compile(r'Hand #([0-9]+): [Zom ]{0,5}Tournament #([0-9]+)')
            name_tournament = compile(r'Tournament #[0-9]+, ([^-]*) - ')
            date_tournament = compile(r'- ([0-9]{4}/[0-9]{2}/[0-9]{2}) ([0-9]{1,2}:[0-9]{2}:[0-9]{2})')
            table_number_and_seats = compile(r"^Table '[0-9]+ ([0-9]+)' ([0-9]+)-max Seat #([0-9]+) is the button$")
            small_and_big_blind = compile(r'\(([0-9]+)/([0-9]+)\)')
            player_init = compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips\)$')
            player_init_sitting_out = compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips\) is sitting out$')
            player_init_out_of_hand = compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips\) out of hand \(')
            player_init_bounty = compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips, \$[0-9.]+ bounty\)$')
            player_init_bounty_out_of_hand = compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips, '
                                                     r'\$[0-9.]+ bounty\) out of hand \(')
            player_init_bounty_sitting_out = compile(r'^Seat ([0-9]+): (' + name + r') \(([0-9]+) in chips, '
                                                     r'\$[0-9.]+ bounty\) is sitting out$')
            find_ante = compile('^(' + name + r'): posts the ante ([0-9]+)$')
            find_ante_all_in = compile('^(' + name + r'): posts the ante ([0-9]+) and is all-in$')
            find_small_blind = compile('^(' + name + r'): posts small blind ([0-9]+)$')
            find_small_blind_all_in = compile('^(' + name + r'): posts small blind ([0-9]+) and is all-in$')
            find_big_blind = compile('^(' + name + r'): posts big blind ([0-9]+)$')
            find_big_blind_all_in = compile('^(' + name + r'): posts big blind ([0-9]+) and is all-in$')
            find_dealt_cards = compile(r'^Dealt to (' + name + r') \[(..) (..)]$')
            find_action = compile('^(' + name + r'): ([a-z0-9 -]+)$')
            find_flop = compile(r'\[(..) (..) (..)]$')
            find_turn = compile(r'\[.. .. ..] \[(..)]$')
            find_river = compile(r'\[.. .. .. ..] \[(..)]$')
            find_shows_in_show_down = compile(r'^(' + name + r'): shows \[(..) (..)] \([a-zA-Z0-9, +-]+\)$')
            find_total_pot = compile(r'^Total pot ([0-9]+) \| Rake [0-9]+$')
            find_total_pot_with_main_pot = compile(r'^Total pot ([0-9]+) Main pot [0-9a-zA-Z.\- ]+ \| Rake [0-9]+$')
            find_collected_pot_summary = compile(r'^Seat [0-9]+: (' + name + r') collected \([0-9]+\)$')
            find_lost = compile(r'^Seat [0-9]+: (' + name + r') showed \[(..) (..)] and lost with')
            find_won = compile(r'^Seat [0-9]+: (' + name + r') showed \[(..) (..)] and won \([0-9]+\) with')
            find_mucked_cards = compile(r'^Seat [0-9]+: (' + name + r') mucked \[(..) (..)]$')
            find_place = compile(r'^([0-9]+)(th|nd|rd|st)$')

            # for processing actions
            find_uncalled_bet = compile(r'^Uncalled bet \(([0-9]+)\) returned to (' + name + r')$')
            find_collect_pot = compile(r'^(' + name + r') collected ([0-9]+) from pot$')
            find_collect_side_pot = compile(r'^(' + name + r') collected ([0-9]+) from side pot$')
            find_collect_side_pot_n = compile(r'^(' + name + r') collected ([0-9]+) from side pot-[0-9]+$')
            find_collect_main_pot = compile(r'^(' + name + r') collected ([0-9]+) from main pot$')
            find_show_cards = compile(r'^(' + name + r'): shows \[([2-9AKQJT hdcs]+)]$')
            find_is_connected = compile(r'^(' + name + r') is connected$')
            find_is_disconnected = compile(r'^(' + name + r') is disconnected$')
            find_is_sitting_out = compile(r'^(' + name + r') is sitting out$')
            find_said = compile(r'^(' + name + ') said, "([^\n]*)"$')
            find_observer_said = compile(r'^(' + name + ') \[observer] said, "([^\n]+)"$')
            find_finished = compile(r'^(' + name + r') finished the tournament in ([0-9]+..) place$')
            find_received = compile(r'^(' + name + r') finished the tournament in ([0-9]+..) place '
                                                   r'and received \$([0-9]+\.[0-9]{2})\.$')
            find_received_fpp = compile(r'^(' + name + r') finished the tournament in ([0-9]+..) place '
                                                       r'and received ([0-9]+) FPP.$')
            find_winner = compile(r'^(' + name + r') wins the tournament and receives '
                                                 r'\$([0-9]+\.[0-9]{2}) - congratulations!$')
            find_does_not_show = compile(r'^(' + name + '): doesn\'t show hand$')
            find_has_returned = compile(r'^(' + name + r') has returned$')
            find_has_timed_out = compile(r'^(' + name + r') has timed out$')
            find_timed_disconnected = compile(r'^(' + name + r') has timed out while disconnected$')
            find_timed_being_disconnected = compile(r'^(' + name + r') has timed out while being disconnected$')
            find_mucks_hand = compile(r'^' + name + r': mucks hand$')
            find_fold_showing_cards = compile(r'^(' + name + r'): folds \[([2-9AKQJT hdcs]+)]$')
            find_finished_the_tournament = compile(r'^(' + name + ') finished the tournament$')
            find_eliminated_and_bounty_first = compile(r'^(' + name + r') wins the \$[0-9.]+ bounty for'
                                                                      r' eliminating (' + name + r')$')
            find_eliminated_and_bounty = compile(r'^(' + name + ') wins \$[0-9.]+ for eliminating (' + name + r') and'
                                                 r' their own bounty increases by \$[0-9.]+ to \$[0-9.]+$')
            find_eliminated_and_bounty_split = compile(r'^(' + name + r') wins \$[0-9.]+ for splitting the '
                                                       r'elimination of (' + name + r') and their own bounty '
                                                       r'increases by \$[0-9.]+ to \$[0-9.]+$')
            find_rebuy_and_receive_chips = compile(r'^(' + name + r') re-buys and receives '
                                                                  r'([0-9]+) chips for \$[0-9.]+$')
            find_rebuy_for_starcoins = compile(r'^(' + name + r') re-buys and receives ([0-9]+) '
                                                              r'chips for ([0-9]+) StarsCoin$')
            find_addon_and_receive_chips = compile(r'^(' + name + r') takes the add-on '
                                                                  r'and receives ([0-9]+) chips for \$[0-9.]+$')
            find_addon_for_starcoins = compile(r'^(' + name + r') takes the add-on and receives ([0-9]+) '
                                                              r'chips for ([0-9]+) StarsCoin$')
            find_skip_break_and_resuming = compile(r'^All players have agreed to skip the break. Game resuming.$')
            find_wins_entry_to_tournament = compile(r'^(' + name + r') wins an entry to tournament #([0-9]+)$')
            find_add_chips = compile(r'^(' + name + r') adds [0-9]+ chips \([0-9]+ stack\(s\) of [0-9]+ chips\). '
                                     r'(' + name + r') has [0-9]+ stack\(s\) remaining.$')
            # TODO : add rebuy, addon, skip break, wins entry to my messages system

        class Poker888:
            name = '[a-zA-Z0-9_\-@\'.,$*`áàåäãçéèêíîóöôõšüúžÄÁÃÅÉÍÖÔÓÜØø´<^>+&' \
                   '\\\/()Ð€£¼ñ®™~#!%\[\]|°¿?:"=ß{}æ©«»¯²¡; ]+'

            identifier = compile('^\*\*\*\*\* 888poker Hand History')
            identifier_snap = compile('^Snap Poker Hand History')

            hand_border = compile('^$')
            hand_border_888 = compile(r'\*\*\*\*\* 888poker Hand History for ')
            hand_border_snap = compile(r'Snap Poker Hand History for ')

            find_hand_id = compile(r'^Game ([0-9]+) \*\*\*\*\*$')
            step_border = compile(r'\*\* [DSa-z ]+ \*\*')

            blinds_and_date = compile(r'^\$([0-9,]+)/\$([0-9,]+) Blinds No Limit Holdem - \*\*\* '
                                      r'(.. .. ....) ([0-9:]+)$')

            blinds_and_ante_2 = compile(r'^([0-9 ]+) \$/([0-9 ]+) \$ Blinds No Limit Holdem - \*\*\* '
                                        r'(.. .. ....) ([0-9:]+)$')

            game_info = compile(r'^Tournament #([0-9]+) (\$[0-9.]+ \+ \$[0-9.]+) - '
                                r'Table #([0-9]+) ([0-9]+) Max \(Real Money\)$')

            game_info_2 = compile(r'^Tournament #([0-9]+) ([0-9,]+ \$ \+ [0-9,]+ \$) - '
                                  r'Table #([0-9]+) ([0-9]+) Max \(Real Money\)$')

            game_info_3 = compile(r'^Tournament #([0-9]+) (\$[0-9.]+) - '
                                  r'Table #([0-9]+) ([0-9]+) Max \(Real Money\)$')

            game_info_4 = compile(r'^Tournament #([0-9]+) ([0-9,]+ \$) - '
                                  r'Table #([0-9]+) ([0-9]+) Max \(Real Money\)$')

            game_info_5 = compile(r'^Tournament #([0-9]+) (Бесплатно) - '
                                  r'Table #([0-9]+) ([0-9]+) Max \(Real Money\)$')

            find_button_seat = compile(r'^Seat ([0-9]+) is the button$')
            player_init = compile(r'^Seat ([0-9]+): (' + name + r') \( \$([0-9,]+) \)$')
            player_init_2 = compile(r'^Seat ([0-9]+): (' + name + r') \( ([0-9 ]+) \$ \)$')
            empty_init = compile(r'^Seat ([0-9]+):[ ]{2}\( ([0-9,$ ]+) \)$')

            find_ante = compile(r'^(' + name + r') posts ante \[\$([0-9,]+)\]$')
            find_ante_2 = compile(r'^(' + name + r') posts ante \[([0-9 ]+) \$\]$')
            find_small_blind = compile(r'^(' + name + ') posts small blind \[\$([0-9,]+)\]$')
            find_small_blind_2 = compile(r'^(' + name + r') posts small blind \[([0-9 ]+) \$\]$')
            find_big_blind = compile(r'^(' + name + ') posts big blind \[\$([0-9,]+)\]$')
            find_big_blind_2 = compile(r'^(' + name + r') posts big blind \[([0-9 ]+) \$\]$')
            find_flop = compile(r'^\[ (..), (..), (..) \]$')
            find_turn = compile(r'^\[ (..) \]$')
            find_river = compile(r'^\[ (..) \]$')
            skip_total_number_of_players = compile(r'^Total number of players : [0-9]+$')

            # actions
            find_dealt_cards = compile(r'^Dealt to (' + name + ') \[ (..), (..) \]$')
            find_fold = compile(r'^(' + name + ') folds$')
            find_call = compile(r'^(' + name + ') calls \[\$([0-9,]+)\]$')
            find_call_2 = compile(r'^(' + name + r') calls \[([0-9 ]+) \$\]$')
            find_check = compile(r'^(' + name + ') checks$')
            find_bet = compile(r'^(' + name + ') bets \[\$([0-9,]+)\]$')
            find_bet_2 = compile(r'^(' + name + r') bets \[([0-9 ]+) \$\]$')
            find_raise = compile(r'^(' + name + ') raises \[\$([0-9,]+)\]$')
            find_raise_2 = compile(r'^(' + name + ') raises \[([0-9 ]+) \$\]$')
            find_did_not_show = compile(r'^(' + name + r') did not show his hand$')
            find_win_money = compile(r'^(' + name + ') collected \[ \$([0-9,]+) \]$')
            find_win_money_2 = compile(r'^(' + name + r') collected \[ ([0-9 ]+) \$ \]$')
            find_show_cards = compile(r'^(' + name + ') shows \[ (..), (..) \]$')
            find_muck_cards = compile(r'^(' + name + ') mucks \[ (..), (..) \]$')

        class PartyPoker:
            name = '[a-zA-Z0-9_\-@\'.,$*`áàåäãçéèêíîóöôõšüúžÄÁÃÅÉÍÖÔÓÜØø´<^>+&' \
                   '\\\/()Ð€£¼ñ®™~#!%\[\]|°¿?:"=ß{}æ©«»¯²¡; ]+'

            identifier = compile('^\*\*\*\*\* Hand History')

            hand_border = compile(r'\*\*\*\*\* Hand History for ')
            step_border = compile(r'\*\* [DFa-z ]+ \*\*')

            find_hand_id = compile(r'^Game ([0-9]+) \*\*\*\*\*$')

            blinds_and_date = compile(r'^NL Texas Hold\'em (\$[0-9.]+ USD) Buy-in Trny:([0-9]+) '
                                      r'Level:[0-9]+[ ]{2}Blinds-Antes\(([0-9 ]+)/([0-9 ]+) -[0-9 ]+\) '
                                      r'- [a-zA-z]+, ([a-zA-z]+) ([0-9]+), ([0-9:]+) CEST ([0-9]+)$')

            blinds_and_date_2 = compile(r'NL Texas Hold\'em (\$[0-9.]+ USD) Buy-in Trny: ([0-9]+) '
                                        r'Level: [0-9]+[ ]{2}Blinds\(([0-9]+)/([0-9]+)\) '
                                        r'- [a-zA-z]+, ([a-zA-z]+) ([0-9]+), ([0-9:]+) CEST ([0-9]+)$')

            table_and_name = compile(r'^Table [a-zA-Z0-9\-\[\] ]+\. ([$0-9.Kx ]+ Gtd)[a-zA-Z0-9- ]+\([0-9]+\) '
                                     r'Table #([0-9]+) \(Real Money\)$')

            find_button = compile(r'^Seat ([0-9]+) is the button$')
            find_seats = compile(r'^Total number of players : [0-9]+/([0-9]+) $')

            player_init = compile(r'^Seat ([0-9]+): (' + name + r') \( ([0-9,]+) \)$')
            skip_tourney = compile(r'^Trny:[ ]?[0-9]+ Level:[ ]?[0-9]+$')
            skip_blinds = compile(r'^Blinds-Antes\([0-9 ]+/[0-9 ]+ -[0-9 ]+\)$')
            skip_blinds_2 = compile(r'^Blinds\([0-9]+/[0-9]+\)$')

            find_ante = compile(r'^(' + name + r') posts ante \[([0-9,]+)\]$')
            find_small_blind = compile(r'^(' + name + r') posts small blind \[([0-9,]+)\]\.$')
            find_big_blind = compile(r'^(' + name + r') posts big blind \[([0-9,]+)\]\.$')
            find_no_small_blind = compile(r'^There is no Small Blind in this hand as the '
                                          r'Big Blind of the previous hand left the table\.$')

            # actions
            find_dealt_cards = compile(r'^Dealt to (' + name + r') \[[ ]{2}(..) (..) \]$')
            find_flop = compile(r'^\[ (..), (..), (..) \]$')
            find_turn = compile(r'^\[ (..) \]$')
            find_river = compile(r'^\[ (..) \]$')
            find_fold = compile(r'^(' + name + r') folds$')
            find_call = compile(r'^(' + name + r') calls \[([0-9,]+)\]$')
            find_check = compile(r'^(' + name + r') checks$')
            find_bet = compile(r'^(' + name + r') bets \[([0-9,]+)\]$')
            find_raise = compile(r'^(' + name + r') raises \[([0-9,]+)\]$')
            find_all_in = compile(r'^(' + name + r') is all-In[ ]{2}\[([0-9,]+)\]$')
            find_did_not_show = compile(r'^(' + name + r') does not show cards\.$')
            find_win_money = compile(r'^(' + name + r') wins ([0-9,]+) chips[a-zA-Z,0-9 ]*\.?$')
            find_show_cards = compile(r'^(' + name + r') shows \[ (..), (..) \][a-zA-Z, ]+\.$')
            find_finished = compile(r'^Player (' + name + r') finished in ([0-9]+)\.$')
            find_knocked_out = compile(r'^(' + name + r') has knocked out (' + name + r') '
                                       r'and won a \$[0-9.]+ USD bounty prize\.$')
            find_join_game = compile(r'^(' + name + r') has joined the table\.$')
            find_use_bank_time = compile(r'^(' + name + r') will be using their time bank for this hand\.$')
            find_did_not_respond = compile(r'^(' + name + r') did not respond in time$')
            find_not_respond_disconnected = compile(r'^(' + name + r') could not respond in time\.\(disconnected\)$')
            find_moved_from_other_table = compile(r'Player (' + name + r') has been '
                                                  r'moved from table [0-9]+ to this table')
            find_break = compile(r'^There will be a break in [0-9]+ minute\(s\)$')
            find_activate_bank = compile(r'^Your time bank will be activated in [0-9]+ secs\. '
                                         r'If you do not want it to be used, please act now\.$')
            find_reconnected = compile(r'^(' + name + r') has been reconnected and has [0-9]+ seconds to act\.$')
            find_chat_message = compile(r'^(' + name + r'): ([^\n]+)$')
            find_disconnected_wait = compile(r'^(' + name + r') is disconnected\. '
                                             r'We will wait for (' + name + r') to reconnect '
                                             r'for a maximum of [0-9]+ seconds\.$')
            find_level_moves = compile(r'^Tournament moves into Level [0-9]+ '
                                       r'and will complete at the end of Level [0-9]+\.$')
            find_end_of_hand = compile(r'^Game #[0-9]+ starts\.$')

    class BaseParsing:

        @staticmethod
        def get_parser(text, game):
            match = GameParser.RegEx.PokerStars.identifier.search(text)
            if match is not None:
                Debug.parser('Found PokerStars game')
                return GameParser.PokerStarsParsing(game)

            match = GameParser.RegEx.Poker888.identifier.search(text)
            if match is not None:
                Debug.parser('Found Poker888 game')
                return GameParser.Poker888Parsing(game)

            match = GameParser.RegEx.Poker888.identifier_snap.search(text)
            if match is not None:
                Debug.parser('Found Poker888 Snap Poker game')
                return GameParser.Poker888Parsing(game)

            match = GameParser.RegEx.PartyPoker.identifier.search(text)
            if match is not None:
                Debug.parser('Found PartyPoker game')
                return GameParser.PartyPokerParsing(game)

            return None

        def __init__(self, parser, game):
            self.parser = parser
            self.game: PokerGame = game
            self.is_broken_hand = True

        def process_game(self, text):
            every_hand = self.split_into_hands(text)
            for hand in every_hand:
                self.process_hand(hand)

        def split_into_hands(self, text):
            # first hand always empty because of separator in start of text
            return self.parser.hand_border.split(text)[1:]

        def split_into_steps(self, text):
            return self.parser.step_border.split(text)

        def process_hand(self, hand):

            steps = self.split_into_steps(hand)

            self.process_initial(steps[0])
            self.process_hole_cards(steps[1])

            if len(steps) == 3:
                self.process_summary(steps[2])

            elif len(steps) == 4:
                self.process_flop(steps[2])
                self.process_summary(steps[3])

            elif len(steps) == 5:
                self.process_flop(steps[2])
                self.process_turn(steps[3])
                self.process_summary(steps[4])

            elif len(steps) == 6:
                self.process_flop(steps[2])
                self.process_turn(steps[3])
                self.process_river(steps[4])
                self.process_summary(steps[5])

            elif len(steps) == 7:
                self.process_flop(steps[2])
                self.process_turn(steps[3])
                self.process_river(steps[4])
                self.process_show_down(steps[5])
                self.process_summary(steps[6])

        def process_initial(self, text):
            pass

        def process_hole_cards(self, text):
            pass

        def process_flop(self, text):
            pass

        def process_turn(self, text):
            pass

        def process_river(self, text):
            pass

        def process_show_down(self, text):
            pass

        def process_summary(self, text):
            pass

    class PokerStarsParsing(BaseParsing):
        def __init__(self, game):
            super().__init__(GameParser.RegEx.PokerStars, game)

        def split_into_hands(self, text):
            every_hand = self.parser.hand_border.split(text)[1:]
            if len(every_hand) == 0:
                every_hand = self.parser.hand_border_2.split(text)
            return every_hand

        @staticmethod
        def parse_action(player: PokerGame.MockPlayer, step: BasePlay.StepType, text: str) \
                -> Tuple[PokerGame.EventType, int]:

            if text == 'folds':
                return PokerGame.Event.Fold, 0

            elif text == 'checks':
                return PokerGame.Event.Check, 0

            elif 'all-in' in text:
                if 'raises' in text:
                    return PokerGame.Event.Allin, int(text.split()[3])

                elif 'bets' in text:
                    return PokerGame.Event.Allin, int(text.split()[1])

                elif 'calls' in text:
                    return PokerGame.Event.Call, int(text.split()[1]) + player.gived(step)

            elif text.startswith('bets'):
                bets, money = text.split()
                return PokerGame.Event.Raise, int(money)

            elif text.startswith('calls'):
                calls, money = text.split()
                return PokerGame.Event.Call, int(money) + player.gived(step)

            elif text.startswith('raises'):
                return PokerGame.Event.Raise, int(text.split()[3])

            else:
                raise ValueError(f'Undefined action: {text}')

        def process_actions(self, lines):
            while True:

                try:
                    line = next(lines).strip()
                except StopIteration:
                    return

                match = self.parser.find_dealt_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    first_card = Card(match.group(2).upper())
                    second_card = Card(match.group(3).upper())
                    pair = CardsPair(first_card, second_card)
                    self.game.curr_hand.set_cards(name, pair)
                    continue

                match = self.parser.find_uncalled_bet.search(line)

                if match is not None:
                    money = int(match.group(1))
                    name = match.group(2)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.ReturnMoney, money)
                    continue

                match = self.parser.find_collect_pot.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    continue

                match = self.parser.find_collect_side_pot.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    continue

                match = self.parser.find_collect_side_pot_n.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    continue

                match = self.parser.find_collect_main_pot.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    continue

                match = self.parser.find_show_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    cards = match.group(2)

                    if len(cards) == 5:
                        card1, card2 = map(str.upper, cards.split())
                        pair = CardsPair(Card(card1), Card(card2))

                    elif len(cards) == 2:
                        only_card = Card(cards.upper())
                        pair = CardsPair(only_card)

                    else:
                        raise ValueError(f'Bad cards shown: {line}')

                    self.game.curr_hand.set_cards(name, pair)
                    continue

                match = self.parser.find_is_connected.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Connected, 0)
                    continue

                match = self.parser.find_is_disconnected.search(line)

                if match is not None:
                    name = match.group(1)
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                    except ValueError:
                        pass
                    continue

                match = self.parser.find_is_sitting_out.search(line)

                if match is not None:
                    name = match.group(1)
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                    except ValueError:
                        pass
                    continue

                match = self.parser.find_said.search(line)

                if match is not None:
                    name = match.group(1)
                    msg = match.group(2)
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.ChatMessage, 0, msg)
                    except ValueError:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.ObserverChatMessage, 0, msg)
                    continue

                match = self.parser.find_observer_said.search(line)

                if match is not None:
                    name = match.group(1)
                    msg = match.group(2)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.ObserverChatMessage, 0, msg)
                    continue

                match = self.parser.find_finished.search(line)

                if match is not None:
                    name = match.group(1)
                    place = match.group(2)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, 0, place)
                    match = self.parser.find_place.search(place)
                    self.game.curr_hand.players_left = int(match.group(1))
                    continue

                match = self.parser.find_received.search(line)

                if match is not None:
                    name = match.group(1)
                    place = match.group(2)
                    earn = int(match.group(3).replace('.', ''))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, earn, place)
                    match = self.parser.find_place.search(place)
                    self.game.curr_hand.players_left = int(match.group(1))
                    continue

                match = self.parser.find_received_fpp.search(line)

                if match is not None:
                    name = match.group(1)
                    place = match.group(2)
                    earn = int(match.group(3))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, earn, place)
                    match = self.parser.find_place.search(place)
                    self.game.curr_hand.players_left = int(match.group(1))
                    continue

                match = self.parser.find_winner.search(line)

                if match is not None:
                    name = match.group(1)
                    earn = int(match.group(2).replace('.', ''))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, earn, '1st')
                    continue

                match = self.parser.find_does_not_show.search(line)

                if match is not None:
                    continue

                match = self.parser.find_has_returned.search(line)

                if match is not None:
                    name = match.group(1)
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.Connected, 0)
                    except ValueError:
                        pass
                    continue

                match = self.parser.find_has_timed_out.search(line)

                if match is not None:
                    continue

                match = self.parser.find_timed_disconnected.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                    continue

                match = self.parser.find_timed_being_disconnected.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                    continue

                match = self.parser.find_finished_the_tournament.search(line)

                if match is not None:
                    continue

                match = self.parser.find_eliminated_and_bounty.search(line)

                if match is not None:
                    continue

                match = self.parser.find_eliminated_and_bounty_first.search(line)

                if match is not None:
                    continue

                match = self.parser.find_eliminated_and_bounty_split.search(line)

                if match is not None:
                    continue

                match = self.parser.find_rebuy_and_receive_chips.search(line)

                if match is not None:
                    continue

                match = self.parser.find_rebuy_for_starcoins.search(line)

                if match is not None:
                    continue

                match = self.parser.find_addon_and_receive_chips.search(line)

                if match is not None:
                    continue

                match = self.parser.find_addon_for_starcoins.search(line)

                if match is not None:
                    continue

                match = self.parser.find_skip_break_and_resuming.search(line)

                if match is not None:
                    continue

                match = self.parser.find_wins_entry_to_tournament.search(line)

                if match is not None:
                    continue

                match = self.parser.find_add_chips.search(line)

                if match is not None:
                    continue

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                    continue

                match = self.parser.find_shows_in_show_down.search(line)

                if match is not None:
                    name = match.group(1)
                    card1 = Card(match.group(2).upper())
                    card2 = Card(match.group(3).upper())
                    self.game.curr_hand.set_cards(name, CardsPair(card1, card2))
                    continue

                match = self.parser.find_fold_showing_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    cards = match.group(2)

                    if len(cards) == 5:
                        card1, card2 = map(str.upper, cards.split())
                        pair = CardsPair(Card(card1), Card(card2))

                    elif len(cards) == 2:
                        only_card = Card(cards.upper())
                        pair = CardsPair(only_card)

                    else:
                        raise ValueError(f'Bad cards shown: {line}')

                    self.game.curr_hand.set_cards(name, pair)
                    continue

                match = self.parser.find_mucks_hand.search(line)

                if match is not None:
                    continue

                match = self.parser.find_action.search(line)

                try:
                    name = match.group(1)
                    action = match.group(2)
                except AttributeError:
                    print('Cannot parse line:', line)
                    raise

                try:
                    result, money = self.parse_action(self.game.curr_hand.get_player(name),
                                                      self.game.curr_hand.curr_step, action)
                except ValueError:
                    print('Bad action: ' + line)
                    raise

                self.game.curr_hand.add_decision(name, result, money)

        def process_initial(self, text):
            every_line: Iterator[str] = iter(text.strip().split('\n'))
            first_line = next(every_line)

            if not first_line.startswith('PokerStars Hand #'):
                raise ValueError('It is not initial step: ' + text)

            match = self.parser.hand_and_game_id.search(first_line)

            try:
                hand_id = int(match.group(1))
            except AttributeError:
                raise ValueError('Bad hand id: ' + first_line)

            if self.game.curr_hand is None:
                id_ = int(match.group(2))

                match = self.parser.name_tournament.search(first_line)

                try:
                    name = match.group(1)
                except AttributeError:
                    raise ValueError('Bad first line: ' + first_line)

                name = name.replace(' USD ', ' ').replace('No Limit', 'NL')

                match = self.parser.date_tournament.search(first_line)
                date = match.group(1)
                time = match.group(2)

                self.game.init(id_, name, 0, date, time)

            match = self.parser.small_and_big_blind.search(first_line)

            small_blind = int(match.group(1))
            big_blind = int(match.group(2))

            line = next(every_line)

            match = self.parser.table_number_and_seats.search(line)

            try:
                table_number = int(match.group(1))
            except AttributeError:
                raise ValueError('Bad table number: ' + line)

            number_of_seats = int(match.group(2))
            button_seat = int(match.group(3))

            if self.game.seats == 0:
                self.game.seats = number_of_seats

            line = next(every_line).strip()
            players: List[PokerGame.MockPlayer] = []
            out_of_hand: List[PokerGame.MockPlayer] = []

            match = self.parser.find_rebuy_and_receive_chips.search(line)
            while match is not None:
                line = next(every_line).strip()
                match = self.parser.find_rebuy_and_receive_chips.search(line)

            match = self.parser.find_rebuy_for_starcoins.search(line)
            while match is not None:
                line = next(every_line).strip()
                match = self.parser.find_rebuy_for_starcoins.search(line)

            match = self.parser.find_addon_and_receive_chips.search(line)
            while match is not None:
                line = next(every_line).strip()
                match = self.parser.find_addon_and_receive_chips.search(line)

            match = self.parser.find_addon_for_starcoins.search(line)
            while match is not None:
                line = next(every_line).strip()
                match = self.parser.find_addon_for_starcoins.search(line)

            while True:

                is_active = False
                is_out_of_hand = False

                match = self.parser.player_init.search(line)
                if match is not None:
                    is_active = True
                    is_out_of_hand = False

                if match is None:
                    match = self.parser.player_init_sitting_out.search(line)
                    if match is not None:
                        is_active = False
                        is_out_of_hand = False

                if match is None:
                    match = self.parser.player_init_out_of_hand.search(line)
                    if match is not None:
                        is_active = True
                        is_out_of_hand = True

                if match is None:
                    match = self.parser.player_init_bounty.search(line)
                    if match is not None:
                        is_active = True
                        is_out_of_hand = False

                if match is None:
                    match = self.parser.player_init_bounty_out_of_hand.search(line)
                    if match is not None:
                        is_active = True
                        is_out_of_hand = True

                if match is None:
                    match = self.parser.player_init_bounty_sitting_out.search(line)
                    if match is not None:
                        is_active = False
                        is_out_of_hand = False

                if match is None:
                    break

                try:
                    seat = int(match.group(1))
                except AttributeError:
                    print('Found bad seat number:', line)
                    raise

                try:
                    name = match.group(2)
                except AttributeError:
                    print('Found bad name:', line)
                    raise

                money = int(match.group(3))
                line = next(every_line).strip()

                if is_out_of_hand:
                    out_of_hand += [PokerGame.MockPlayer(name, money, seat, is_active)]
                else:
                    players += [PokerGame.MockPlayer(name, money, seat, is_active)]

            self.game.add_hand(players)
            self.game.curr_hand.id = hand_id
            self.game.curr_hand.small_blind = small_blind
            self.game.curr_hand.big_blind = big_blind
            self.game.curr_hand.sit_during_game = out_of_hand
            self.game.curr_hand.table_id = table_number
            self.game.curr_hand.button_seat = button_seat

            match = self.parser.find_skip_break_and_resuming.search(line)
            if match is not None:
                line = next(every_line)

            while True:

                is_all_in = False

                match = self.parser.find_ante_all_in.search(line)

                if match is not None:
                    is_all_in = True

                if match is None:
                    match = self.parser.find_ante.search(line)

                if match is None:
                    break

                name = match.group(1)
                ante = int(match.group(2))

                if self.game.curr_hand.ante == 0:
                    self.game.curr_hand.ante = ante

                self.game.curr_hand.add_decision(name, PokerGame.Event.Ante, ante)

                if is_all_in:
                    self.game.curr_hand.set_all_in(name)

                line = next(every_line)

            while True:

                is_all_in = False

                match = self.parser.find_small_blind_all_in.search(line)

                if match is not None:
                    is_all_in = True

                if match is None:
                    match = self.parser.find_small_blind.search(line)

                if match is None:
                    break

                name = match.group(1)
                small_blind = int(match.group(2))

                self.game.curr_hand.add_decision(name, PokerGame.Event.SmallBlind, small_blind)

                try:
                    line = next(every_line)
                except StopIteration:
                    all_in_name = self.game.curr_hand.get_only_all_in()
                    self.game.curr_hand.add_decision(all_in_name, PokerGame.Event.BigBlind, 0)

                if is_all_in:
                    self.game.curr_hand.set_all_in(name)

                break

            while True:

                is_all_in = False

                match = self.parser.find_big_blind_all_in.search(line)

                if match is not None:
                    is_all_in = True

                if match is None:
                    match = self.parser.find_big_blind.search(line)

                if match is None:
                    break

                name = match.group(1)
                big_blind = int(match.group(2))

                self.game.curr_hand.add_decision(name, PokerGame.Event.BigBlind, big_blind)

                if is_all_in:
                    self.game.curr_hand.set_all_in(name)

                break

            self.process_actions(every_line)

        def process_hole_cards(self, text: str) -> None:
            every_line = iter(text.strip().split('\n'))
            self.process_actions(every_line)

        def process_flop(self, text: str) -> None:
            self.game.curr_hand.switch_to_step(BasePlay.Step.Flop)

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_flop.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process flop: {text}')

            flop1 = Card(match.group(1).upper())
            flop2 = Card(match.group(2).upper())
            flop3 = Card(match.group(3).upper())

            self.game.curr_hand.set_flop_cards(flop1, flop2, flop3)

            self.process_actions(every_line)

        def process_turn(self, text: str) -> None:
            self.game.curr_hand.switch_to_step(BasePlay.Step.Turn)

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_turn.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process turn: {text}')

            turn_card = Card(match.group(1).upper())
            self.game.curr_hand.set_turn_card(turn_card)

            self.process_actions(every_line)

        def process_river(self, text: str) -> None:
            self.game.curr_hand.switch_to_step(BasePlay.Step.River)

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_river.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process river: {text}')

            river_card = Card(match.group(1).upper())
            self.game.curr_hand.set_river_card(river_card)

            self.process_actions(every_line)

        def process_show_down(self, text: str) -> None:
            every_line = iter(text.strip().split('\n'))
            self.game.curr_hand.goes_to_showdown = True
            self.process_actions(every_line)

        def process_summary(self, text: str) -> None:
            every_line = iter(text.strip().split('\n'))
            line = next(every_line).strip()

            if not line.startswith('Total pot'):
                raise ValueError(f'Bad first line of summary: {text}')

            if 'Main pot' in line:
                match = self.parser.find_total_pot_with_main_pot.search(line)
            else:
                match = self.parser.find_total_pot.search(line)

            try:
                total_pot = int(match.group(1))
            except AttributeError:
                raise ValueError(f'Bad total pot: {line}')

            self.game.curr_hand.total_pot = total_pot

            line = next(every_line)

            if line.startswith('Board'):
                line = next(every_line)

            if not line.startswith('Seat'):
                raise ValueError(f'Bad second/third line of summary: {text}')

            while line.startswith('Seat'):

                if line.endswith("folded before Flop (didn't bet)") or \
                        line.endswith('folded before Flop') or \
                        line.endswith('folded on the Flop') or \
                        line.endswith('folded on the Turn') or \
                        line.endswith('folded on the River'):

                    try:
                        line = next(every_line)
                    except StopIteration:
                        return

                    continue

                if ' (button) ' in line:
                    line = line.replace(' (button) ', ' ')
                if ' (big blind) ' in line:
                    line = line.replace(' (big blind) ', ' ')
                if ' (small blind) ' in line:
                    line = line.replace(' (small blind) ', ' ')

                match = self.parser.find_collected_pot_summary.search(line)

                if match is not None:

                    name = match.group(1)
                    win_player_cards = self.game.curr_hand.get_player(name).cards
                    if win_player_cards is not None and win_player_cards.initialized():
                        self.game.curr_hand.add_winner(name)

                else:

                    match = self.parser.find_lost.search(line)

                    if match is not None:
                        name = match.group(1)
                        card1 = Card(match.group(2).upper())
                        card2 = Card(match.group(3).upper())
                        self.game.curr_hand.set_cards(name, CardsPair(card1, card2))
                        self.game.curr_hand.add_loser(name)

                    else:

                        match = self.parser.find_won.search(line)

                        if match is not None:
                            name = match.group(1)
                            card1 = Card(match.group(2).upper())
                            card2 = Card(match.group(3).upper())
                            self.game.curr_hand.set_cards(name, CardsPair(card1, card2))
                            self.game.curr_hand.add_winner(name)

                        else:

                            match = self.parser.find_mucked_cards.search(line)

                            if match is not None:
                                name = match.group(1)
                                card1 = Card(match.group(2).upper())
                                card2 = Card(match.group(3).upper())
                                self.game.curr_hand.set_cards(name, CardsPair(card1, card2))
                                self.game.curr_hand.add_loser(name)

                            else:
                                raise ValueError(f'Bad summary processing line: {line}')

                try:
                    line = next(every_line)
                except StopIteration:
                    return

            self.process_actions(every_line)

    class Poker888Parsing(BaseParsing):
        def __init__(self, game, is_snap=False):
            super().__init__(GameParser.RegEx.Poker888, game)
            self.call_amount = 0
            self.total_pot = 0
            if is_snap:
                self.parser.hand_border = self.parser.hand_border_snap
            else:
                self.parser.hand_border = self.parser.hand_border_888

        def process_actions(self, lines):
            while True:

                try:
                    line = next(lines).strip()
                except StopIteration:
                    return
                
                if len(line) == 0:
                    return

                match = self.parser.find_dealt_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    first_card = Card(match.group(2).upper())
                    second_card = Card(match.group(3).upper())
                    pair = CardsPair(first_card, second_card)
                    self.game.curr_hand.set_cards(name, pair)
                    continue

                match = self.parser.find_fold.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Fold, 0)
                    continue

                match = self.parser.find_call.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.total_pot += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Call, self.call_amount)
                    continue

                match = self.parser.find_call_2.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace('\xa0', ''))
                    self.total_pot += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Call, self.call_amount)
                    continue

                match = self.parser.find_check.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Check, 0)
                    continue

                match = self.parser.find_bet.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.call_amount = money
                    self.total_pot += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, money)
                    continue

                match = self.parser.find_bet_2.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace('\xa0', ''))
                    self.call_amount = money
                    self.total_pot += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, money)
                    continue

                match = self.parser.find_raise.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.total_pot += money
                    self.call_amount += money
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, self.call_amount)
                    except ValueError:
                        print('Can not add decision: ' + line)
                        raise
                    continue

                match = self.parser.find_raise_2.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace('\xa0', ''))
                    self.total_pot += money
                    self.call_amount += money
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, self.call_amount)
                    except ValueError:
                        print('Can not add decision: ' + line)
                        raise
                    continue

                match = self.parser.find_did_not_show.search(line)

                if match is not None:
                    continue

                match = self.parser.find_win_money.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    self.game.curr_hand.add_winner(name)
                    continue

                match = self.parser.find_win_money_2.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace('\xa0', ''))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    self.game.curr_hand.add_winner(name)
                    continue

                match = self.parser.find_show_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    card1 = Card(match.group(2).upper())
                    card2 = Card(match.group(3).upper())
                    pair = CardsPair(card1, card2)
                    self.game.curr_hand.set_cards(name, pair)
                    self.game.curr_hand.goes_to_showdown = True
                    continue

                match = self.parser.find_muck_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    card1 = Card(match.group(2).upper())
                    card2 = Card(match.group(3).upper())
                    pair = CardsPair(card1, card2)
                    self.game.curr_hand.set_cards(name, pair)
                    self.game.curr_hand.add_loser(name)
                    continue

                raise ValueError('Undefined action: ' + line)

        def process_initial(self, text: str):
            lines = iter(text.strip().split('\n'))
            line = next(lines)
            self.is_broken_hand = False

            match = self.parser.find_hand_id.search(line)
            hand_id = int(match.group(1))

            line = next(lines).strip()

            match = self.parser.blinds_and_date.search(line)

            if match is None:
                match = self.parser.blinds_and_ante_2.search(line)

            try:
                small_blind = int(match.group(1).replace(',', '').replace('\xa0', ''))
            except AttributeError:
                print('Bad blinds: ' + line)
                raise
            big_blind = int(match.group(2).replace(',', '').replace('\xa0', ''))
            self.call_amount = big_blind
            date = '/'.join(match.group(3).split()[::-1])
            time = match.group(4)

            line = next(lines)

            match = self.parser.game_info.search(line)

            if match is None:
                match = self.parser.game_info_2.search(line)

            if match is None:
                match = self.parser.game_info_3.search(line)

            if match is None:
                match = self.parser.game_info_4.search(line)

            if match is None:
                match = self.parser.game_info_5.search(line)

            if self.game.curr_hand is None:
                try:
                    self.game.init(
                        int(match.group(1)),
                        'NL ' + match.group(2),
                        int(match.group(4)),
                        date, time
                    )
                except AttributeError:
                    raise ValueError('Bad game init line: ' + line)

            table_number = match.group(3)

            line = next(lines)

            match = self.parser.find_button_seat.search(line)

            button_seat = int(match.group(1))

            line = next(lines)

            match = self.parser.skip_total_number_of_players.search(line)

            if match is None:
                raise ValueError('Bad skip: ' + line)

            line = next(lines).strip()

            players: List[PokerGame.MockPlayer] = []
            out_of_hand: List[PokerGame.MockPlayer] = []

            while True:
                is_active = True
                is_out_of_hand = False

                match = self.parser.player_init.search(line)

                if match is None:
                    match = self.parser.player_init_2.search(line)

                if match is None:
                    break

                seat = int(match.group(1))
                name = match.group(2)
                money = int(match.group(3).replace(',', '').replace('\xa0', ''))

                if is_out_of_hand:
                    out_of_hand += [PokerGame.MockPlayer(name, money, seat, is_active)]
                else:
                    players += [PokerGame.MockPlayer(name, money, seat, is_active)]

                line = next(lines).strip()

            if len(players) == 0:

                if not self.parser.empty_init.search(line):
                    raise ValueError('Can not parse player: ' + line)

                self.is_broken_hand = True
                return

            self.game.add_hand(players)
            self.game.curr_hand.init(hand_id, small_blind, big_blind, out_of_hand, table_number, button_seat)

            while True:
                match = self.parser.find_ante.search(line)

                if match is None:
                    match = self.parser.find_ante_2.search(line)

                if match is None:
                    break

                name = match.group(1)
                ante = int(match.group(2).replace(',', '').replace('\xa0', ''))

                self.total_pot += ante

                if self.game.curr_hand.ante == 0:
                    self.game.curr_hand.ante = ante

                self.game.curr_hand.add_decision(name, PokerGame.Event.Ante, ante)

                line = next(lines)

            while True:
                match = self.parser.find_small_blind.search(line)

                if match is None:
                    match = self.parser.find_small_blind_2.search(line)
                    
                if match is None:
                    break

                name = match.group(1)
                small_blind = int(match.group(2).replace(',', '').replace('\xa0', ''))

                self.total_pot += small_blind

                self.game.curr_hand.add_decision(name, PokerGame.Event.SmallBlind, small_blind)

                try:
                    line = next(lines)
                except StopIteration:
                    all_in_game = self.game.curr_hand.get_only_all_in()
                    self.game.curr_hand.add_decision(all_in_game, PokerGame.Event.BigBlind, 0)

                break

            while True:
                match = self.parser.find_big_blind.search(line)

                if match is None:
                    match = self.parser.find_big_blind_2.search(line)
                    
                if match is None:
                    break

                name = match.group(1)
                big_blind = int(match.group(2).replace(',', '').replace('\xa0', ''))

                self.total_pot += big_blind

                self.game.curr_hand.add_decision(name, PokerGame.Event.BigBlind, big_blind)

                break

            self.process_actions(lines)

        def process_hole_cards(self, text: str) -> None:
            if self.is_broken_hand:
                return
            every_line = iter(text.strip().split('\n'))
            self.process_actions(every_line)

        def process_flop(self, text: str):
            if self.is_broken_hand:
                return
            self.game.curr_hand.switch_to_step(BasePlay.Step.Flop)
            self.call_amount = 0

            lines = iter(text.strip().split('\n'))
            line = next(lines)

            match = self.parser.find_flop.search(line)

            if match is None:
                raise ValueError(f'Bad first line in process flop: {text}')

            flop1 = Card(match.group(1).upper())
            flop2 = Card(match.group(2).upper())
            flop3 = Card(match.group(3).upper())

            self.game.curr_hand.set_flop_cards(flop1, flop2, flop3)

            self.process_actions(lines)

        def process_turn(self, text: str) -> None:
            if self.is_broken_hand:
                return
            self.game.curr_hand.switch_to_step(BasePlay.Step.Turn)
            self.call_amount = 0

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_turn.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process turn: {text}')

            turn_card = Card(match.group(1).upper())
            self.game.curr_hand.set_turn_card(turn_card)

            self.process_actions(every_line)

        def process_river(self, text: str) -> None:
            if self.is_broken_hand:
                return
            self.game.curr_hand.switch_to_step(BasePlay.Step.River)
            self.call_amount = 0

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_river.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process river: {text}')

            river_card = Card(match.group(1).upper())
            self.game.curr_hand.set_river_card(river_card)

            self.process_actions(every_line)

        def process_summary(self, text: str) -> None:
            if self.is_broken_hand:
                return
            every_line = iter(text.strip().split('\n'))
            self.game.curr_hand.total_pot = self.total_pot
            self.process_actions(every_line)

    class PartyPokerParsing(BaseParsing):
        def __init__(self, game):
            super().__init__(GameParser.RegEx.PartyPoker, game)
            self.call_amount = 0
            self.total_pot = 0

        def process_actions(self, lines):
            while True:

                try:
                    line = next(lines).strip()
                except StopIteration:
                    return

                if len(line) == 0:
                    return

                match = self.parser.find_dealt_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    first_card = Card(match.group(2).upper())
                    second_card = Card(match.group(3).upper())
                    pair = CardsPair(first_card, second_card)
                    self.game.curr_hand.set_cards(name, pair)
                    continue

                match = self.parser.find_fold.search(line)

                if match is not None:
                    name = match.group(1)
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.Fold, 0)
                    except ValueError:
                        pass
                    continue

                match = self.parser.find_call.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.total_pot += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Call, self.call_amount)
                    continue

                match = self.parser.find_check.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Check, 0)
                    continue

                match = self.parser.find_bet.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.call_amount = money
                    self.total_pot += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, money)
                    continue

                match = self.parser.find_raise.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.total_pot += money
                    self.call_amount += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, self.call_amount)
                    continue

                match = self.parser.find_all_in.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.total_pot += money
                    self.call_amount += money
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Raise, self.call_amount)
                    continue

                match = self.parser.find_did_not_show.search(line)

                if match is not None:
                    continue

                match = self.parser.find_win_money.search(line)

                if match is not None:
                    name = match.group(1)
                    money = int(match.group(2).replace(',', ''))
                    self.game.curr_hand.add_decision(name, PokerGame.Event.WinMoney, money)
                    self.game.curr_hand.add_winner(name)
                    continue

                match = self.parser.find_show_cards.search(line)

                if match is not None:
                    name = match.group(1)
                    card1 = Card(match.group(2).upper())
                    card2 = Card(match.group(3).upper())
                    pair = CardsPair(card1, card2)
                    self.game.curr_hand.set_cards(name, pair)
                    self.game.curr_hand.goes_to_showdown = True
                    continue

                match = self.parser.find_finished.search(line)

                if match is not None:
                    name = match.group(1)
                    place = match.group(2)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.FinishGame, 0, place)
                    continue

                match = self.parser.find_knocked_out.search(line)

                if match is not None:
                    continue

                match = self.parser.find_join_game.search(line)

                if match is not None:
                    continue

                match = self.parser.find_use_bank_time.search(line)

                if match is not None:
                    continue

                match = self.parser.find_did_not_respond.search(line)

                if match is not None:
                    continue

                match = self.parser.find_not_respond_disconnected.search(line)

                if match is not None:
                    name = match.group(1)
                    self.game.curr_hand.add_decision(name, PokerGame.Event.Disconnected, 0)
                    continue

                match = self.parser.find_moved_from_other_table.search(line)

                if match is not None:
                    continue

                match = self.parser.find_break.search(line)

                if match is not None:
                    continue

                match = self.parser.find_activate_bank.search(line)

                if match is not None:
                    continue

                match = self.parser.find_reconnected.search(line)

                if match is not None:
                    continue

                match = self.parser.find_disconnected_wait.search(line)

                if match is not None:
                    continue

                match = self.parser.find_level_moves.search(line)

                if match is not None:
                    continue

                match = self.parser.find_chat_message.search(line)

                if match is not None:
                    name = match.group(1)
                    message = match.group(2)
                    try:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.ChatMessage, 0, message)
                    except ValueError:
                        self.game.curr_hand.add_decision(name, PokerGame.Event.ObserverChatMessage, 0, message)
                    continue

                match = self.parser.find_end_of_hand.search(line)

                if match is not None:
                    self.game.curr_hand.total_pot = self.total_pot
                    break

                raise ValueError('Undefined action: ' + line)

        def process_initial(self, text: str):
            lines = iter(text.strip().split('\n'))
            line = next(lines)
            self.is_broken_hand = False

            match = self.parser.find_hand_id.search(line)
            hand_id = int(match.group(1))

            line = next(lines).strip()

            match = self.parser.blinds_and_date.search(line)

            if match is None:
                match = self.parser.blinds_and_date_2.search(line)

            try:
                name = match.group(1)
            except AttributeError:
                raise ValueError('Bad name: ' + line)
            game_id = match.group(2)

            small_blind = int(match.group(3).replace(' ', ''))
            big_blind = int(match.group(4).replace(' ', ''))

            month = f'{month_name[:].index(match.group(5)):>02}'
            day = match.group(6)
            year = match.group(8)

            date = f'{year}/{month}/{day}'
            time = match.group(7)

            self.call_amount = big_blind

            line = next(lines)

            match = self.parser.table_and_name.search(line)

            try:
                name += ' ' + match.group(1)
            except AttributeError:
                raise ValueError('Bad game name: ' + line)
            table_number = match.group(2)

            line = next(lines)

            match = self.parser.find_button.search(line)

            button_seat = int(match.group(1))

            line = next(lines)

            match = self.parser.find_seats.search(line)

            seats = int(match.group(1))

            if self.game.curr_hand is None:
                self.game.init(game_id, name, seats, date, time)

            line = next(lines).strip()

            players: List[PokerGame.MockPlayer] = []
            out_of_hand: List[PokerGame.MockPlayer] = []

            while True:
                is_active = True
                is_out_of_hand = False

                match = self.parser.player_init.search(line)

                if match is None:
                    break

                seat = int(match.group(1))
                name = match.group(2)
                money = int(match.group(3).replace(',', ''))

                if is_out_of_hand:
                    out_of_hand += [PokerGame.MockPlayer(name, money, seat, is_active)]
                else:
                    players += [PokerGame.MockPlayer(name, money, seat, is_active)]

                line = next(lines).strip()

            if len(players) == 0:
                raise ValueError('Can not parse player: ' + line)

            self.game.add_hand(players)
            self.game.curr_hand.init(hand_id, small_blind, big_blind, out_of_hand, table_number, button_seat)

            match = self.parser.skip_tourney.search(line)
            if match is None:
                raise ValueError('Skip error 1: ' + line)

            line = next(lines)
            match = self.parser.skip_blinds.search(line)
            if match is None:
                match = self.parser.skip_blinds_2.search(line)

            if match is None:
                raise ValueError('Skip error 2: ' + line)

            line = next(lines)

            while True:
                match = self.parser.find_ante.search(line)

                if match is None:
                    break

                name = match.group(1)
                ante = int(match.group(2).replace(',', ''))

                if self.game.curr_hand.ante == 0:
                    self.game.curr_hand.ante = ante

                self.total_pot += ante

                self.game.curr_hand.add_decision(name, PokerGame.Event.Ante, ante)

                line = next(lines)

            while True:
                match = self.parser.find_small_blind.search(line)

                if match is None:
                    match = self.parser.find_no_small_blind.search(line)
                    if match is not None:
                        line = next(lines)
                        break

                if match is None:
                    break

                name = match.group(1)
                small_blind = int(match.group(2).replace(',', ''))

                self.total_pot += small_blind

                self.game.curr_hand.add_decision(name, PokerGame.Event.SmallBlind, small_blind)

                try:
                    line = next(lines)
                except StopIteration:
                    all_in_game = self.game.curr_hand.get_only_all_in()
                    self.game.curr_hand.add_decision(all_in_game, PokerGame.Event.BigBlind, 0)

                break

            while True:
                match = self.parser.find_big_blind.search(line)

                if match is None:
                    break

                name = match.group(1)
                big_blind = int(match.group(2).replace(',', ''))

                self.total_pot += big_blind

                self.game.curr_hand.add_decision(name, PokerGame.Event.BigBlind, big_blind)

                break

            self.process_actions(lines)

        def process_hole_cards(self, text: str) -> None:
            every_line = iter(text.strip().split('\n'))
            self.process_actions(every_line)

        def process_flop(self, text: str):
            self.game.curr_hand.switch_to_step(BasePlay.Step.Flop)
            self.call_amount = 0

            lines = iter(text.strip().split('\n'))
            line = next(lines)

            match = self.parser.find_flop.search(line)

            if match is None:
                raise ValueError(f'Bad first line in process flop: {text}')

            flop1 = Card(match.group(1).upper())
            flop2 = Card(match.group(2).upper())
            flop3 = Card(match.group(3).upper())

            self.game.curr_hand.set_flop_cards(flop1, flop2, flop3)

            self.process_actions(lines)

        def process_turn(self, text: str) -> None:
            self.game.curr_hand.switch_to_step(BasePlay.Step.Turn)
            self.call_amount = 0

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_turn.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process turn: {text}')

            turn_card = Card(match.group(1).upper())
            self.game.curr_hand.set_turn_card(turn_card)

            self.process_actions(every_line)

        def process_river(self, text: str) -> None:
            self.game.curr_hand.switch_to_step(BasePlay.Step.River)
            self.call_amount = 0

            every_line = iter(text.strip().split('\n'))
            first_line = next(every_line)

            match = self.parser.find_river.search(first_line)

            if match is None:
                raise ValueError(f'Bad first line in process river: {text}')

            river_card = Card(match.group(1).upper())
            self.game.curr_hand.set_river_card(river_card)

            self.process_actions(every_line)

    @staticmethod
    def parse_dir(path: str) -> None:
        games = listdir(PokerGame.path_to_raw_games + path)
        if not exists(PokerGame.path_to_parsed_games + path):
            makedirs(PokerGame.path_to_parsed_games + path)
        for game_path in games:
            game = GameParser.parse_game(f'{path}/{game_path}')
            if game is not None:
                game.save()
                # game.convert()
                remove(PokerGame.path_to_raw_games + path + '/' + game_path)

    @staticmethod
    def parse_game(path: str) -> Optional[PokerGame]:
        game = PokerGame()
        text_game = open(PokerGame.path_to_raw_games + path, 'r', encoding='utf-8').read().strip()
        game.source = path

        Debug.parser('\nStarting to analyse ' + path)

        parser = GameParser.BaseParsing.get_parser(text_game, game)

        if parser is None:
            Debug.parser('Cannot parse game - can not identify')
            return None

        parser.process_game(text_game)

        game.approximate_players_left()
        game.add_final_table_marks()
        return game


class GameManager:

    def __init__(self):

        self.network: Network = Network('ge', 'main')
        self.game: Game = None

    def run(self):

        Thread(target=lambda: self.infinite(), name='GameManager infinite').start()

    def create_game(self, real, bots, seats, stack, scheme, name=''):

        real = int(real)
        bots = int(bots)
        seats = int(seats)
        stack = int(stack)

        self.network.send_raw('http name:' + name)
        self.network.send_raw('http players:' + str(real+bots))

        if scheme == 'standard':
            scheme = Blinds.Scheme.Standard

        elif scheme == 'fast':
            scheme = Blinds.Scheme.Fast

        elif scheme == 'rapid':
            scheme = Blinds.Scheme.Rapid

        elif scheme == 'bullet':
            scheme = Blinds.Scheme.Bullet

        else:
            return

        self.game = Game(real + bots, seats, stack, scheme)

        for _ in range(bots):
            self.game.add_player()

        self.network.send_raw('http start_registration')

    def add_player(self, name) -> None:

        if self.game.add_player(name):
            self.network.send_raw('http start')
            Thread(target=lambda: self.wait_for_end(), name='GameManager: wait for end').start()

    def delete_player(self, name) -> None:

        self.game.delete_player(name)

    def wait_for_end(self) -> None:

        self.game.thread.join()

        if not self.game.game_broken:
            del self.game
            self.game = None
            self.network.send_raw('http end')

    def break_game(self):

        self.game.break_game()

        if self.game.thread:
            self.game.thread.join()

        del self.game
        self.game = None
        self.network.send_raw('http broken')

    def infinite(self):

        Debug.game_manager('Game manager: ready to listen')

        while True:

            try:

                request = self.network.receive_raw()

                Debug.game_manager('Game manager: message "' + request + '"')

                request = request.split()

                if request[0] == 'create' and self.game is None:
                    Debug.game_manager('Game manager: create game')
                    self.create_game(*request[1:])
                    Debug.game_manager('Game manager: game created')

                elif request[0] == 'add' and self.game is not None and not self.game.game_started:
                    Debug.game_manager('Game manager: add player')
                    self.add_player(request[1])
                    Debug.game_manager('Game manager: player added')

                elif request[0] == 'delete' and self.game is not None and not self.game.game_started:
                    Debug.game_manager('Game manager: delete player')
                    self.delete_player(request[1])
                    Debug.game_manager('Game manager: player deleted')

                elif request[0] == 'break' and self.game is not None:
                    Debug.game_manager('Game manager: break game')
                    self.break_game()
                    Debug.game_manager('Game manager: game broken')

            except ValueError:
                continue

            except IndexError:
                continue


class Evolution:

    def __init__(self, games: int, seats: int, players: int, money: int,
                 blinds_scheme: Blinds.SchemeType = Blinds.Scheme.Standard):

        self.games: int = games
        self.players: int = players
        self.seats: int = seats
        self.money: int = money
        self.blinds_scheme: Blinds.SchemeType = blinds_scheme
        Play.EvolutionMode = True

    def run(self) -> None:

        for num in range(self.games):

            game = Game(self.players, self.seats, self.money, self.blinds_scheme)

            for _ in range(game.total_players):
                game.add_player()

            Debug.evolution(f'Start game #{num + 1}')

            while not game.game_finished:
                sleep(1)

            PlayManager.standings(10)
            PlayManager.delete_bad_plays()


class Run:

    def __init__(self, mode: BasePlay.ModeType):

        Play.Mode = mode
        if mode == BasePlay.Mode.GameEngine:
            # PlayManager.standings()
            GameManager().run()

        elif mode == BasePlay.Mode.Parse:
            GameParser.parse_dir('pack1')
            # game.save()
            # game.convert()
            # print(game)

        elif mode == BasePlay.Mode.Evolution:
            PlayManager.standings()
            Evolution(100000, 9, 999, 10000, Blinds.Scheme.Rapid).run()

        elif mode == BasePlay.Mode.Testing:
            NeuralNetwork.PokerDecision.Bubble(100, 9).show()


if __name__ == '__main__':
    Run(BasePlay.Mode.Parse)
