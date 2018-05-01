from re import compile


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
    skip_blinds = compile(r'^Blinds-Antes\(([0-9 ]+)/([0-9 ]+) -([0-9 ]+)\)$')
    skip_blinds_2 = compile(r'^Blinds\(([0-9]+)/([0-9]+)\)$')

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
