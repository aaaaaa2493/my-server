from typing import List, Tuple
from threading import Thread
from time import sleep
from holdem.game import Game


class Blinds:

    SchemeType = dict

    class Scheme:

        OrderType = List[Tuple[int, int, int]]

        class Order:

            Standard = [(5, 10, 0), (10, 20, 0), (20, 40, 0), (40, 80, 0),
                        (60, 120, 0), (80, 160, 0), (120, 240, 0), (160, 320, 0),
                        (180, 360, 0), (220, 440, 10), (300, 600, 30), (400, 800, 50),
                        (500, 1000, 100), (700, 1400, 200), (1000, 2000, 300),
                        (1500, 3000, 400), (2000, 4000, 500), (3000, 6000, 700),
                        (4000, 8000, 900), (6000, 12000, 1200), (8000, 16000, 1600),
                        (10000, 20000, 2000), (15000, 30000, 3000), (20000, 40000, 4000),
                        (30000, 60000, 6000), (40000, 80000, 8000), (60000, 120000, 12000),
                        (100000, 200000, 20000), (150000, 300000, 30000),
                        (200000, 400000, 50000), (300000, 600000, 80000),
                        (400000, 800000, 120000), (600000, 1200000, 160000),
                        (800000, 1600000, 220000), (1000000, 2000000, 300000)]

        TimeType = int

        class Time:
            Standard = 15
            Fast = 8
            Rapid = 3
            Bullet = 1

        HandsType = int

        class Hands:
            Standard = 75
            Fast = 40
            Rapid = 20
            Bullet = 5

        Standard = {'order': Order.Standard,
                    'time': Time.Standard,
                    'hands': Hands.Standard}

        Fast = {'order': Order.Standard,
                'time': Time.Fast,
                'hands': Hands.Fast}

        Rapid = {'order': Order.Standard,
                 'time': Time.Rapid,
                 'hands': Hands.Rapid}

        Bullet = {'order': Order.Standard,
                  'time': Time.Bullet,
                  'hands': Hands.Bullet}

    def __init__(self, scheme: 'Blinds.SchemeType', game: 'Game'):

        self.game: Game = game
        self.thread: Thread = None

        self.order: Blinds.Scheme.OrderType = scheme['order']
        self.hands: Blinds.Scheme.HandsType = scheme['hands']
        self.time: Blinds.Scheme.TimeType = scheme['time']

        self.curr_round: int = -1
        self.to_next_round: int = 1

        self.small_blind: int = self.order[0][0]
        self.big_blind: int = self.order[0][1]
        self.ante: int = self.order[0][2]

    def set_blinds(self) -> None:

        self.small_blind = self.order[self.curr_round][0]
        self.big_blind = self.order[self.curr_round][1]
        self.ante = self.order[self.curr_round][2]

    def next_hand(self) -> bool:

        self.to_next_round -= 1

        if self.to_next_round == 0 and self.curr_round < len(self.order) - 1:
            self.curr_round += 1
            self.to_next_round = self.hands
            self.set_blinds()
            return True

        return False

    def start(self) -> None:

        self.thread = Thread(target=lambda: self.infinite(), name='Blinds infinite')
        self.thread.start()

    def infinite(self) -> None:

        self.curr_round += 1

        while self.curr_round < len(self.order) - 1 and not self.game.game_finished and not self.game.game_broken:

            sleep(self.time * 60)

            self.curr_round += 1
            self.set_blinds()

            if not self.game.game_finished and not self.game.game_broken:

                self.game.blinds_increased()
