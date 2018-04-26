from re import compile


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
