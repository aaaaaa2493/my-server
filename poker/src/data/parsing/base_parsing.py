from data.poker_game import PokerGame


class BaseParsing:

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
