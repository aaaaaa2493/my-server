from enum import Enum


class Mode(Enum):
    Evolution = 0
    Parse = 1
    GameEngine = 2
    Testing = 3


class Settings:
    game_mode: Mode
