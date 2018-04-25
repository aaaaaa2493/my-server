from enum import Enum


class Time(Enum):
    Standard = 15
    Fast = 8
    Rapid = 3
    Bullet = 1

    def to_int(self) -> int:
        return self.value
