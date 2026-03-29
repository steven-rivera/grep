from .match import Match, MatchState
from .parser import Parser
from .nodes import Node
from typing import Iterator


class Pattern:
    def __init__(self, pattern: str, num_groups: int, ast: Node):
        self.pattern = pattern
        self._num_groups = num_groups
        self._ast = ast

    def search(self, s: str) -> Match | None:
        """
        Scan through string looking for the first location where the regular
        expression pattern produces a match, and return a corresponding Match.
        Return None if no position in the string matches the pattern.
        """
        return next(self._find_all_generator(s), None)

    def findall(self, s: str) -> list[Match]:
        """
        Return all non-overlapping matches of pattern in string, as a list of Matches.
        The string is scanned left-to-right, and matches are returned in the order found.
        """
        return [match for match in self._find_all_generator(s)]

    def match(self, s: str) -> Match | None:
        """
        If zero or more characters at the beginning of string match the regular
        expression pattern, return a corresponding Match. Return None if the
        string does not match the pattern.
        """

        return next(self._find_all_generator(s, stop=1), None)

    def fullmatch(self, s: str) -> Match | None:
        """
        If the whole string matches the regular expression pattern, return a
        corresponding Match. Return None if the string does not match the pattern.
        """
        match = self.match(s)
        if match is not None and len(s) == len(match.match):
            return match
        return None

    def _find_all_generator(self, s: str, stop: int = -1) -> Iterator[Match]:
        if stop == -1:
            stop = len(s)

        i = 0
        while i < stop:
            match_states = self._ast.match(s, MatchState(i, {}))

            if len(match_states) == 0:
                i += 1
                continue

            ms = match_states[-1]
            m = Match(
                match=s[i : ms.pos],
                span=(i, ms.pos),
                captures=ms.captures,
                string=s,
                _num_groups=self._num_groups,
            )

            yield m

            i = max(ms.pos, i + 1)


def compile(pattern: str) -> Pattern:
    parser = Parser(pattern)
    ast, num_groups = parser.parse()

    return Pattern(pattern=pattern, ast=ast, num_groups=num_groups)
