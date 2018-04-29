from numpy import array


class BasePokerDecision:

    def __init__(self):
        self.answer: float = 0

    def to_array(self) -> array:
        raise NotImplementedError('to array')
