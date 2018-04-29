from numpy import array


class BasePokerDecision:

    def __init__(self):
        pass

    def to_array(self) -> array:
        raise NotImplementedError('to array')
