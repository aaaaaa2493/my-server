from typing import Optional, List, Tuple
from json import loads, dumps
from websocket import create_connection
from holdem.base_play import Result, Step
from holdem.board import Board
from holdem.holdem_poker import Hand
from special.debug import Debug
from core.card import Card


class Network:

    if Debug.Debug:
        ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'

    port = 9001

    def __init__(self, identifier: dict, is_dummy: bool = False, need_disconnect_info: bool = True):

        self.is_dummy = is_dummy
        self.need_disconnect_info = need_disconnect_info

        if not is_dummy:
            self.socket = create_connection(f'ws://{Network.ip}:{Network.port}')
            self.socket.send(dumps(identifier))

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

            if decision[0] == Result.Fold:
                curr['type'] = 'fold'

            elif decision[0] == Result.Check:
                curr['type'] = 'check'

            elif decision[0] == Result.Call:
                curr['type'] = 'call'
                curr['money'] = decision[1]

            elif decision[0] == Result.Raise:
                curr['type'] = 'raise'
                curr['from'] = decision[1]
                curr['to'] = decision[2]

            elif decision[0] == Result.Allin:
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

    def init_hand(self, player: Optional['Player'], table: 'Table', game: 'Game') -> Optional[str]:

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

    def ante(self, all_paid: List[Tuple['Player', int]]) -> Optional[str]:

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

    def blinds(self, button: 'Player', blind_info: List[Tuple['Player', int]]) -> Optional[str]:

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

    def give_cards(self, player: 'Player') -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'give cards'
        to_send['first'] = player.cards.first.card
        to_send['second'] = player.cards.second.card

        return self.send_raw(f'give_cards {player.id} {dumps(to_send)}')

    def deal_cards(self) -> Optional[str]:

        return self.send({'type': 'deal cards'})

    def delete_player(self, player: 'Player') -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'delete player'
        to_send['id'] = player.id

        return self.send(to_send)

    def add_player(self, player: 'Player', seat: int) -> Optional[str]:

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

    def resit(self, player: 'Player', players: 'Players') -> Optional[str]:

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
            return self.send_raw(f'resit {players.game.id} {players.id} {dumps(to_send)}')
        else:
            return self.send(to_send)

    def switch_decision(self, player: 'Player') -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'switch decision'
        to_send['id'] = player.id

        return self.send(to_send)

    def made_decision(self, player: 'Player', decision: Result) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'made decision'

        if decision == Result.Fold:
            to_send['result'] = 'fold'

        elif decision == Result.Check:
            to_send['result'] = 'check'

        elif decision == Result.Call:
            to_send['result'] = 'call'
            to_send['money'] = player.gived

        elif decision == Result.Raise:
            to_send['result'] = 'raise'
            to_send['money'] = player.gived

        elif decision == Result.Allin:
            to_send['result'] = 'all in'
            to_send['money'] = player.gived

        else:
            raise ValueError(f'I FORGOT ABOUT RESULT ID {decision}')

        return self.send(to_send)

    def back_excess_money(self, player: 'Player', money: int) -> Optional[str]:

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

    def open_cards(self, table: 'Table', for_replay=False) -> Optional[str]:

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

    def give_money(self, player: 'Player', money: int) -> Optional[str]:

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

    def hand_results(self, board: Board, results: List[Tuple[Hand, 'Player', str]]) -> Optional[str]:

        to_send = dict()

        to_send['type'] = 'hand results'

        if board.state == Step.Preflop:
            to_send['flop1'] = Card.UndefinedCard
            to_send['flop2'] = Card.UndefinedCard
            to_send['flop3'] = Card.UndefinedCard
            to_send['turn'] = Card.UndefinedCard
            to_send['river'] = Card.UndefinedCard

        elif board.state == Step.Flop:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = Card.UndefinedCard
            to_send['river'] = Card.UndefinedCard

        elif board.state == Step.Turn:
            to_send['flop1'] = board.flop1.card
            to_send['flop2'] = board.flop2.card
            to_send['flop3'] = board.flop3.card
            to_send['turn'] = board.turn.card
            to_send['river'] = Card.UndefinedCard

        elif board.state == Step.River:
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
