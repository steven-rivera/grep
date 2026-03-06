from dataclasses import dataclass

@dataclass
class Match:
    match: str
    span: tuple[int, int]
    captures: dict[int, tuple[int, int]]

    def start(self) -> int:
        return self.span[0]

    def end(self) -> int:
        return self.span[1]


@dataclass
class MatchState:
    # Current position in the string
    pos: int
    # Keys are group ID's and values are the start and end index of captured group
    captures: dict[int, tuple[int, int]]
