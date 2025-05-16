from dataclasses import dataclass

from models.wrestler import Wrestler


@dataclass
class Match:
    type: str
    result: str
    won: float
    cagematch: float
    wrestlers: list[Wrestler]
    teams: list[Wrestler]
    appearances: list[Wrestler]
