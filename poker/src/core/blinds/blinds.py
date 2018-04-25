from core.blinds.scheme.scheme import Scheme, Order, Hands, Time


class Blinds:

    def __init__(self, scheme: Scheme):
        self.order: Order = scheme.order
        self.hands: Hands = scheme.hands
        self.time: Time = scheme.time

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
        self.next_hand()
