from re import compile
from typing import Tuple, Iterator, List, Optional
from os import listdir, makedirs, remove
from os.path import exists
from calendar import month_name
from parsing.poker_game import PokerGame
from holdem.play.step import Step
from holdem.cards_pair import CardsPair
from special.debug import Debug
from core.cards.card import Card


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
