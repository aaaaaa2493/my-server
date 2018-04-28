from typing import Tuple, Iterator, List
from core.cards.cards_pair import Card, CardsPair
from data.parsing.base_parsing import BaseParsing
from data.reg_ex.poker_stars import PokerStars
from data.game_model.poker_game import PokerGame
from holdem.play.step import Step


class PokerStarsParsing(BaseParsing):
    def __init__(self, game):
        super().__init__(PokerStars, game)

    def split_into_hands(self, text):
        every_hand = self.parser.hand_border.split(text)[1:]
        if not every_hand:
            every_hand = self.parser.hand_border_2.split(text)
        return every_hand

    @staticmethod
    def parse_action(player: PokerGame.MockPlayer, step: Step, text: str) \
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
            _, money = text.split()
            return PokerGame.Event.Raise, int(money)

        elif text.startswith('calls'):
            _, money = text.split()
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
        self.game.curr_hand.switch_to_step(Step.Flop)

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
        self.game.curr_hand.switch_to_step(Step.Turn)

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
