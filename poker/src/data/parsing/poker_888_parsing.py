from typing import List
from core.cards.cards_pair import Card, CardsPair
from data.parsing.base_parsing import BaseParsing
from data.reg_ex.poker_888 import Poker888
from data.game_model.poker_game import PokerGame
from holdem.play.step import Step


class Poker888Parsing(BaseParsing):
    def __init__(self, game, is_snap=False):
        super().__init__(Poker888, game)
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

            if not line:
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

        if not players:

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
        self.game.curr_hand.switch_to_step(Step.Flop)
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
        self.game.curr_hand.switch_to_step(Step.Turn)
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
        self.game.curr_hand.switch_to_step(Step.River)
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
