from core.blinds.blinds import Blinds


class AbstractGame:
    def __init__(self, id_: int, blinds: Blinds):
        self.id: int = id_
        self.blinds: Blinds = blinds
        self.game_started: bool = False
        self.game_finished: bool = False
        self.game_broken: bool = False
        self.online: bool = False

    def blinds_increased(self):
        raise NotImplementedError('Blinds increased')
