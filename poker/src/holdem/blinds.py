from typing import List, Tuple
from threading import Thread
from time import sleep


class Blinds:

    SchemeType = dict

    class Scheme:

        OrderType = List[Tuple[int, int, int]]

        class Order:

            Standard = [
                (5, 10, 0),
                (10, 20, 0),
                (20, 40, 0),
                (40, 80, 0),
                (60, 120, 0),
                (80, 160, 0),
                (120, 240, 0),
                (160, 320, 0),
                (180, 360, 0),
                (220, 440, 10),
                (300, 600, 30),
                (400, 800, 50),
                (500, 1_000, 100),
                (700, 1_400, 200),
                (1_000, 2_000, 300),
                (1_500, 3_000, 400),
                (2_000, 4_000, 500),
                (3_000, 6_000, 700),
                (4_000, 8_000, 900),
                (6_000, 12_000, 1_200),
                (8_000, 16_000, 1_600),
                (10_000, 20_000, 2_000),
                (15_000, 30_000, 3_000),
                (20_000, 40_000, 4_000),
                (30_000, 60_000, 6_000),
                (40_000, 80_000, 8_000),
                (60_000, 120_000, 12_000),
                (100_000, 200_000, 20_000),
                (150_000, 300_000, 30_000),
                (200_000, 400_000, 50_000),
                (300_000, 600_000, 80_000),
                (400_000, 800_000, 120_000),
                (600_000, 1_200_000, 160_000),
                (800_000, 1_600_000, 220_000),
                (1_000_000, 2_000_000, 300_000)
            ]

            WSOP = [
                (75, 150, 0),
                (150, 300, 0),
                (150, 300, 25),
                (200, 400, 50),
                (250, 500, 75),
                (300, 600, 100),
                (400, 800, 125),
                (500, 1_000, 150),
                (600, 1_200, 200),
                (800, 1_600, 250),
                (1_000, 2_000, 300),
                (1_200, 2_400, 400),
                (1_500, 3_000, 500),
                (2_000, 4_000, 650),
                (2_500, 5_000, 800),
                (3_000, 6_000, 1_000),
                (4_000, 8_000, 1_300),
                (5_000, 10_000, 1_600),
                (6_000, 12_000, 2_000),
                (8_000, 16_000, 2_500),
                (10_000, 20_000, 3_000),
                (12_000, 24_000, 4_000),
                (15_000, 30_000, 5_000),
                (20_000, 40_000, 6_500),
                (25_000, 50_000, 8_000),
                (30_000, 60_000, 10_000),
                (40_000, 80_000, 12_500),
                (50_000, 100_000, 15_000),
                (60_000, 120_000, 20_000),
                (80_000, 160_000, 25_000),
                (100_000, 200_000, 30_000),
                (120_000, 240_000, 40_000),
                (150_000, 300_000, 50_000),
                (200_000, 400_000, 60_000),
                (250_000, 500_000, 75_000),
                (300_000, 600_000, 100_000),
                (400_000, 800_000, 125_000),
                (500_000, 1_000_000, 150_000),
                (600_000, 1_200_000, 200_000),
                (800_000, 1_600_000, 250_000),
                (1_000_000, 2_000_000, 300_000),
                (1_200_000, 2_400_000, 400_000),
                (1_500_000, 3_000_000, 500_000),
                (2_000_000, 4_000_000, 600_000),
                (2_500_000, 5_000_000, 750_000),
                (3_000_000, 6_000_000, 1_000_000),
                (4_000_000, 8_000_000, 1_250_000),
                (5_000_000, 10_000_000, 1_500_000)
            ]

            Static = [(5, 10, 1)]

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

        Static = {'order': Order.Static,
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

        self.game: 'Game' = game
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

        self.thread = Thread(target=self.infinite, name='Blinds infinite')
        self.thread.start()

    def infinite(self) -> None:

        self.curr_round += 1

        while self.curr_round < len(self.order) - 1 and (
                not self.game.game_finished and not self.game.game_broken):

            sleep(self.time * 60)

            self.curr_round += 1
            self.set_blinds()

            if not self.game.game_finished and not self.game.game_broken:

                self.game.blinds_increased()
