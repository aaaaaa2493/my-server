from typing import List
from calendar import month_name
from core.cards.cards_pair import Card, CardsPair
from data.parsing.base_parsing import BaseParsing
from data.reg_ex.party_poker import PartyPoker
from data.game_model.poker_game import PokerGame
from holdem.play.step import Step


class PartyPokerParsing(BaseParsing):
    def __init__(self, game):
        super().__init__(PartyPoker, game)
        self.call_amount = 0
        self.total_pot = 0

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

        if not players:
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
