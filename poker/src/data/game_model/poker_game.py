from typing import List, Tuple, Iterator, Dict
from os import mkdir, makedirs, listdir
from os.path import exists
from pickle import load, dump
from json import loads, dumps
from datetime import datetime, timedelta
from shutil import rmtree
from statistics import mean
from holdem.play.step import Step
from holdem.network import Network
from holdem.game.game import Game
from holdem.player import Player
from holdem.table import Delay
from holdem.poker.hand_strength import HandStrength
from holdem.poker.hand import Hand
from data.game_model.poker_hand import PokerHand
from data.game_model.mock_player import MockPlayer
from data.game_model.event import Event


class PokerGame:
    path_to_raw_games = 'games/raw/'
    path_to_parsed_games = 'games/parsed/'
    path_to_converted_games = 'games/converted/'

    def __init__(self):
        self.id: int = 0
        self.name: str = ''
        self.date: str = ''
        self.time: str = ''
        self.source: str = ''
        self.seats: int = 0
        self.hands: List[PokerHand] = []
        self.curr_hand: PokerHand = None

    def init(self, id_, name, seats, date, time):
        self.id = id_
        self.name = name
        self.seats = seats
        self.date = date
        self.time = time

    def add_hand(self, players: List[MockPlayer]):
        new_hand = PokerHand(players)
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
        *dirs, _ = path.split('/')

        dirs = '/'.join(dirs)

        if not exists(dirs):
            makedirs(dirs)

        dump(self, open(path, 'wb'))

    @staticmethod
    def load_dir(path: str) -> List['PokerGame']:
        games = []
        for curr_path in listdir(PokerGame.path_to_parsed_games + path):
            games += [PokerGame.load(path + '/' + curr_path)]
        return games

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
        network = Network({}, True, False)
        chat_messages: List[Tuple[datetime, str]] = []

        for num, hand in enumerate(self.hands):

            converted: List[Tuple[datetime, str]] = []
            hand.switch_to_step(Step.Preflop)
            events: Iterator[Event] = iter(hand.curr_events)

            game = Game(0, self.seats, self.seats, 0)
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
                    new_player = Player(0, player.seat, player.name, player.money, True, True)
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
            time = time + timedelta(seconds=Delay.InitHand)

            converted += [(time, network.deal_cards())]
            time = time + timedelta(seconds=0)

            converted += [(time, network.open_cards(table))]
            time = time + timedelta(seconds=Delay.DealCards)

            event = next(events)

            if hand.ante > 0:

                paid: List[Tuple[Player, int]] = []
                while event.event == Event.Ante:
                    paid += [(find[event.player.seat], event.money)]
                    event = next(events)

                converted += [(time, network.ante(paid))]
                time = time + timedelta(seconds=Delay.Ante)

                converted += [(time, network.collect_money())]
                time = time + timedelta(seconds=Delay.CollectMoney)

            button: Player = find[hand.button_seat]

            blinds_info: List[Tuple[Player, int]] = []

            if event.event == Event.SmallBlind:
                blinds_info += [(find[event.player.seat], event.money)]
                event = next(events)

            if event.event == Event.BigBlind:
                blinds_info += [(find[event.player.seat], event.money)]
                event = next(events)

            converted += [(time, network.blinds(button, blinds_info))]
            time = time + timedelta(seconds=Delay.Blinds)

            if hand.sit_during_game:

                for player in hand.sit_during_game:
                    converted += [(time, network.add_player(Player(0, player.seat, player.name,
                                                                   player.money, True, True), player.seat - 1))]
                    time = time + timedelta(seconds=Delay.AddPlayer)

            avoid_in_first_iteration = True
            need_to_collect_money = True

            while True:

                if hand.curr_step == Step.River:
                    break

                elif not avoid_in_first_iteration:

                    hand.next_step()

                    need_to_continue = False

                    if hand.curr_step == Step.Flop and \
                            hand.board.flop1 is not None and \
                            hand.board.flop2 is not None and \
                            hand.board.flop3 is not None:
                        converted += [(time, network.flop(hand.board.flop1, hand.board.flop2, hand.board.flop3))]
                        time = time + timedelta(seconds=Delay.Flop)
                        need_to_continue = True

                    elif hand.curr_step == Step.Turn and hand.board.turn is not None:
                        converted += [(time, network.turn(hand.board.turn))]
                        time = time + timedelta(seconds=Delay.Turn)
                        need_to_continue = True

                    elif hand.curr_step == Step.River and hand.board.river is not None:
                        converted += [(time, network.river(hand.board.river))]
                        time = time + timedelta(seconds=Delay.River)
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

                    if event.event == Event.Fold or \
                            event.event == Event.Check or \
                            event.event == Event.Call or \
                            event.event == Event.Raise or \
                            event.event == Event.Allin:

                        if event.event == Event.Call or \
                                event.event == Event.Raise or \
                                event.event == Event.Allin:
                            need_to_collect_money = True

                        player = find[event.player.seat]
                        player.gived = event.money

                        converted += [(time, network.switch_decision(player))]
                        time = time + timedelta(seconds=Delay.SwitchDecision + Delay.DummyMove)

                        converted += [(time, network.made_decision(player, Event.ToResult[event.event]))]
                        time = time + timedelta(seconds=Delay.MadeDecision)

                    elif event.event == Event.WinMoney:

                        if need_to_collect_money:
                            converted += [(time, network.collect_money())]
                            time = time + timedelta(seconds=Delay.CollectMoney)
                            need_to_collect_money = False

                        converted += [(time, network.give_money(find[event.player.seat], event.money))]
                        time = time + timedelta(seconds=Delay.GiveMoney)

                    elif event.event == Event.ReturnMoney:

                        if sum(e.event == Event.Allin or
                               e.event == Event.Raise or
                               e.event == Event.Call or
                               e.event == Event.SmallBlind or
                               e.event == Event.BigBlind for e in hand.curr_events) == 1:
                            need_to_collect_money = False

                        converted += [(time, network.back_excess_money(find[event.player.seat], event.money))]
                        time = time + timedelta(seconds=Delay.ExcessMoney)

                    elif event.event == Event.ChatMessage:

                        chat_message = network.send({'type': 'chat', 'text': f'{event.player.name}: {event.message}'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == Event.ObserverChatMessage:

                        chat_message = network.send({'type': 'chat',
                                                     'text': f'{event.player.name} [observer]: {event.message}'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == Event.Disconnected:

                        converted += [(time, network.send({'type': 'disconnected', 'id': event.player.seat}))]
                        time = time + timedelta(seconds=0)

                        chat_message = network.send({'type': 'chat', 'text': f'{event.player.name} disconnected'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == Event.Connected:

                        converted += [(time, network.send({'type': 'connected', 'id': event.player.seat}))]
                        time = time + timedelta(seconds=0)

                        chat_message = network.send({'type': 'chat', 'text': f'{event.player.name} connected'})

                        converted += [(time, chat_message)]
                        chat_messages += [(time, chat_message)]

                        time = time + timedelta(seconds=0)

                    elif event.event == Event.FinishGame:

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
                            time = time + timedelta(seconds=Delay.DeletePlayer)

                    else:
                        raise ValueError(f'Undefined event id {event.event}')

                    try:
                        event = next(events)
                    except StopIteration:

                        time = time + timedelta(seconds=Delay.EndOfRound)

                        if need_to_collect_money:
                            converted += [(time, network.collect_money())]
                            time = time + timedelta(seconds=Delay.CollectMoney)
                            need_to_collect_money = False

                        break

            results: List[Tuple[Hand, Player, str]] = []

            for player in hand.players:
                if player.cards is not None:
                    if hand.board.state == Step.Preflop:
                        if not player.cards.initialized():
                            curr_hand = HandStrength.strength1(player.cards.first)
                        else:
                            curr_hand = HandStrength.strength2(player.cards.first, player.cards.second)

                    elif hand.board.state == Step.Flop:
                        if not player.cards.initialized():
                            curr_hand = HandStrength.strength4(player.cards.first, hand.board.flop1,
                                                               hand.board.flop2, hand.board.flop3)
                        else:
                            curr_hand = HandStrength.strength(player.cards.first, player.cards.second,
                                                              hand.board.flop1, hand.board.flop2, hand.board.flop3)

                    else:
                        cards = hand.board.get()

                        if not player.cards.initialized():
                            cards += [player.cards.first]
                        else:
                            cards += [player.cards.first, player.cards.second]

                        curr_hand = HandStrength.max_strength(cards)

                    results += [(curr_hand, find[player.seat], '')]

            results.sort(reverse=True, key=lambda x: x[0])

            converted += [(time, network.hand_results(hand.board, results))]
            time = time + timedelta(seconds=Delay.HandResults)

            converted += [(time, network.clear())]
            time = time + timedelta(seconds=Delay.Clear)

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
