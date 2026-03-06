from .match import Match, MatchState
from .parser import Parser
from . import nodes


class Pattern:
    def __init__(self, pattern: str, numGroups: int, ast: nodes.Node):
        self.pattern = pattern
        self._numGroups = numGroups
        self._ast = ast

    def search(self, s: str) -> Match | None:
        i = 0
        while i < len(s):
            matchStates = self._ast.match(s, MatchState(i, {}))
            if len(matchStates) > 0:
                # Pick first match
                matchState = matchStates[0]
                return Match(
                    span=(i, matchState.pos),
                    match=s[i : matchState.pos],
                    captures=matchState.captures,
                )

            i += 1

        return None

    def match(self, s: str) -> Match | None:
        matchStates = self._ast.match(s, MatchState(0, {}))
        if len(matchStates) > 0:
            # Pick first match
            matchState = matchStates[0]
            return Match(
                span=(0, matchState.pos),
                match=s[0 : matchState.pos],
                captures=matchState.captures,
            )
        return None

    def fullmatch(self, s: str) -> Match | None:
        match = self.match(s)
        if match is not None and len(s) == len(match.match):
            return match
        return None

    def findall(self, s: str) -> list[Match]:
        matches = []

        i = 0
        while i < len(s):
            matchStates = self._ast.match(s, MatchState(i, {}))
            if len(matchStates) > 0:
                # Pick longest match
                matchState = matchStates[-1]
                matches.append(
                    Match(
                        span=(i, matchState.pos),
                        match=s[i : matchState.pos],
                        captures=matchState.captures,
                    )
                )
                i = max(matchState.pos, i + 1)
            else:
                i += 1

        return matches


def compile(pattern: str) -> Pattern:
    parser = Parser(pattern)
    ast, numGroups = parser.parse()

    return Pattern(pattern=pattern, ast=ast, numGroups=numGroups)
