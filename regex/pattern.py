from .match import Match, MatchState
from .parser import Parser
from .nodes import Node
from typing import Iterator


class Pattern:
    def __init__(self, pattern: str, numGroups: int, ast: Node):
        self.pattern = pattern
        self._numGroups = numGroups
        self._ast = ast

    def search(self, s: str) -> Match | None:
        gen = self._find_all(s, stop=len(s))
        return next(gen, None)

    def findall(self, s: str) -> list[Match]:
        return [match for match in self._find_all(s, stop=len(s))]

    def match(self, s: str) -> Match | None:
        gen = self._find_all(s, stop=1)
        return next(gen, None)

    def fullmatch(self, s: str) -> Match | None:
        match = self.match(s)
        if match is not None and len(s) == len(match.match):
            return match
        return None

    def _find_all(self, s: str, stop: int) -> Iterator[Match]:
        i = 0
        while i < stop:
            match_states = self._ast.match(s, MatchState(i, {}))

            if len(match_states) == 0:
                i += 1
                continue

            ms = match_states[-1]
            m = Match(
                span=(i, ms.pos),
                match=s[i : ms.pos],
                captures=ms.captures,
                string=s
            )

            yield m

            i = max(ms.pos, i + 1)


def compile(pattern: str) -> Pattern:
    parser = Parser(pattern)
    ast, numGroups = parser.parse()

    return Pattern(pattern=pattern, ast=ast, numGroups=numGroups)
