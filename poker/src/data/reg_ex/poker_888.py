from re import compile


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
