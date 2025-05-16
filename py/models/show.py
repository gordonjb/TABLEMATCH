from dataclasses import dataclass

from models.match import Match
from models.promotion import Promotion


@dataclass
class Show:
    id: list[str]
    name: str
    promotion: Promotion
    arena: str
    date: str
    matches: list[Match]
    partial: bool = False
    exclude: bool = False
