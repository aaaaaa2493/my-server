from enum import Enum
from core.blinds.scheme.scheme import Scheme, Order, Time, Hands


class Schemes(Enum):
    Standard: Scheme = Scheme(Order.Standard, Time.Standard, Hands.Standard)
    Static: Scheme = Scheme(Order.Static, Time.Standard, Hands.Standard)
    Fast: Scheme = Scheme(Order.Standard, Time.Fast, Hands.Fast)
    Rapid: Scheme = Scheme(Order.Standard, Time.Rapid, Hands.Rapid)
    Bullet: Scheme = Scheme(Order.Standard, Time.Bullet, Hands.Bullet)
