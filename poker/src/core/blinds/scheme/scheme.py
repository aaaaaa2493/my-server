from core.blinds.scheme.order import Order
from core.blinds.scheme.time import Time
from core.blinds.scheme.hands import Hands


class Scheme:
    def __init__(self, order: Order, time: Time, hands: Hands):
        self.order: Order = order
        self.time: Time = time
        self.hands: Hands = hands
