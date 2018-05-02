from enum import Enum
from core.blinds.scheme.scheme import Scheme
from core.blinds.scheme.hands import Hands
from core.blinds.scheme.time import Time
from core.blinds.scheme.order import Order


class Schemes(Enum):
    Standard: Scheme = Scheme(Order.Standard, Time.Standard, Hands.Standard)
    Static: Scheme = Scheme(Order.Static, Time.Standard, Hands.Standard)
    Fast: Scheme = Scheme(Order.Standard, Time.Fast, Hands.Fast)
    Rapid: Scheme = Scheme(Order.Standard, Time.Rapid, Hands.Rapid)
    Bullet: Scheme = Scheme(Order.Standard, Time.Bullet, Hands.Bullet)
