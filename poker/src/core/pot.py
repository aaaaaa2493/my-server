class Pot:

    def __init__(self):
        self.money: int = 0

    def __str__(self):
        return str(self.money)

    def __bool__(self):
        return self.money
