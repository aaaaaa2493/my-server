from typing import List, Tuple
from threading import Thread, Lock
from time import sleep
from holdem.base_play import Result, Step
from holdem.cards_pair import CardsPair
from holdem.players import Players
from holdem.blinds import Blinds
from holdem.board import Board
from holdem.holdem_poker import HoldemPoker as Poker
from holdem.network import Network
from holdem.delay import Delay
from special.debug import Debug
from core.card import Card
from core.deck import Deck
from core.pot import Pot


class Table:

    Tables = List['Table']

    class History:

        Decisions = List['Table.History.Decision']

        class Decision:

            def __init__(self, player: 'Player', decision: Result, money: int):

                self.player: 'Player' = player
                self.decision: Result = decision
                self.money: int = money

            def __str__(self):
                return f'{self.player.cards} {self.player.id:>3} ' \
                       f'{Result.ToStr[self.decision]:<5} {self.money}'

        Steps = List['Table.History.Step']

        class Step:

            def __init__(self):

                self.decisions: Table.History.Decisions = []

            def add(self, player: 'Player', decision: Result, money: int) -> None:

                self.decisions += [Table.History.Decision(player, decision, money)]

        Hands = List['Table.History.Hands']

        class Hand:

            def __init__(self, number: int):

                self.number = number
                self.opened_cards: Card.Cards = None
                self.dealt_cards: List[Tuple['Player', CardsPair]] = None
                self.last_step: Step = Step.Preflop

                self.preflop: Table.History.Step = Table.History.Step()
                self.flop: Table.History.Step = None
                self.turn: Table.History.Step = None
                self.river: Table.History.Step = None

            def add(self, player: 'Player', result: Result, money: int) -> None:

                if self.last_step == Step.River:
                    self.river.add(player, result, money)

                elif self.last_step == Step.Turn:
                    self.turn.add(player, result, money)

                elif self.last_step == Step.Flop:
                    self.flop.add(player, result, money)

                elif self.last_step == Step.Preflop:
                    self.preflop.add(player, result, money)

                else:
                    raise OverflowError('Undefined step')

            def give_cards(self, players: Players) -> None:

                self.dealt_cards = []

                for player in players.all_players():
                    self.dealt_cards += [(player, player.cards)]

            def next_step(self) -> None:

                if self.last_step == Step.Turn:
                    self.river = Table.History.Step()
                    self.last_step = Step.River

                elif self.last_step == Step.Flop:
                    self.turn = Table.History.Step()
                    self.last_step = Step.Turn

                elif self.last_step == Step.Preflop:
                    self.flop = Table.History.Step()
                    self.last_step = Step.Flop

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

        def add(self, player: 'Player', result: Result, money: int) -> None:

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
        self.players: Players = Players(game, seats, _id, is_final)
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
                self.history.add(player, Result.Ante, paid)
                Debug.table(f'Table {self.id} hand {self.board.hand}: player {player.name} paid ante {paid}')

            if self.online:
                self.network.ante(all_paid)
                sleep(Delay.Ante)
                self.network.collect_money()
                sleep(Delay.CollectMoney)

    def collect_blinds(self, sb: int, bb: int) -> None:

        self.players.to_button_seat()

        if self.players.count == 2:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            paid1 = player1.pay_blind(sb)
            self.history.add(player1, Result.SmallBlind, paid1)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player1.name} paid small blind {paid1}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(bb)
            self.history.add(player2, Result.BigBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid big blind {paid2}')

            if self.online:
                self.network.blinds(player1, [(player1, paid1), (player2, paid2)])
                sleep(Delay.Blinds)

        elif self.players.game_without_small_blind and self.players.next_seat() is None:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(bb)
            self.history.add(player2, Result.BigBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid big blind {paid2}')

            if self.online:
                self.network.blinds(player1, [(player2, paid2)])
                sleep(Delay.Blinds)

        else:
            player1 = self.players.to_button()
            Debug.table(f'Table {self.id} hand {self.board.hand}: button on {player1.name}')
            player2 = self.players.next_player()
            paid2 = player2.pay_blind(sb)
            self.history.add(player2, Result.SmallBlind, paid2)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player2.name} paid small blind {paid2}')
            player3 = self.players.next_player()
            paid3 = player3.pay_blind(bb)
            self.history.add(player3, Result.BigBlind, paid3)
            Debug.table(f'Table {self.id} hand {self.board.hand}: player {player3.name} paid big blind {paid3}')

            if self.online:
                self.network.blinds(player1, [(player2, paid2), (player3, paid3)])
                sleep(Delay.Blinds)

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
                sleep(Delay.CollectMoney)

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
            sleep(Delay.DealCards)

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
            sleep(Delay.InitHand)

        if not self.first_hand:
            self.players.move_button()
        else:
            self.first_hand = False

        self.players.lock.acquire()

        ante = self.blinds.ante
        sb = self.blinds.small_blind
        bb = self.blinds.big_blind

        self.collect_ante(ante)

        for step in Step:

            if step == Step.Preflop:

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
                        sleep(Delay.SwitchDecision)

                    result = player.decide(step, to_call, can_raise_from, self.board.get(), self.online)

                    if self.online:
                        self.network.made_decision(player, result)
                        sleep(Delay.MadeDecision)

                    player.history.set(step, result, self.raise_counter, player.in_all_in())
                    self.history.add(player, result, player.gived)

                    if result == Result.Raise or result == Result.Allin:

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
                sleep(Delay.EndOfRound)

            if self.players.count_in_game_players() == 1:

                player_max_pot = max(p for p in self.players.in_game_players())
                second_max_pot = max(p.gived for p in self.players.all_players() if p != player_max_pot)
                difference = player_max_pot.gived - second_max_pot
                player_max_pot.gived -= difference
                player_max_pot.money += difference

                if self.online:
                    self.network.back_excess_money(player_max_pot, difference)
                    sleep(Delay.ExcessMoney)

                self.history.add(player_max_pot, Result.ReturnMoney, difference)
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
                        sleep(Delay.ExcessMoney)

                    self.history.add(player, Result.ReturnMoney, difference)
                    Debug.table(f'Table {self.id} hand {self.board.hand}: {difference} money back to {player.name}')

                self.collect_pot()

                if self.online:
                    self.network.open_cards(self)
                    sleep(Delay.OpenCards)

                self.board.open_all_with_network(self)
                self.end_game()
                return

            if step == Step.Preflop:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open flop')
            elif step == Step.Flop:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open turn')
            elif step == Step.Turn:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open river')
            elif step == Step.River:
                Debug.table(f'Table {self.id} hand {self.board.hand}: open cards')

                self.collect_pot()

                if self.online:
                    self.network.open_cards(self)
                    sleep(Delay.OpenCards)

                self.end_game()
                return

            self.collect_pot()

            self.board.open_with_network(self)
            self.history.next_step()
            Debug.table(f'Table {self.id} hand {self.board.hand}: board {self.board}')

    def give_money(self, winner: 'Player') -> None:

        winner.in_pot = 0
        winner.money += winner.wins
        self.pot.money -= winner.wins

        self.history.add(winner, Result.WinMoney, winner.wins)

        if self.online:
            self.network.give_money(winner, winner.wins)
            sleep(Delay.GiveMoney)

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
            sleep(Delay.MoneyResults)

    def take_cards(self) -> None:

        for player in self.players.all_players():
            player.drop_cards()

        if self.online:
            self.network.clear()
            sleep(Delay.Clear)

        self.board.clear()

    def end_game(self) -> None:

        Debug.table(f'Table {self.id} hand {self.board.hand}: cards - {self.board}')

        if self.players.count_in_game_players() == 1:

            if self.online:
                self.network.hand_results(self.board, [])
                sleep(Delay.HandResults)

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
                sleep(Delay.HandResults)

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

                if all_inners:
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
