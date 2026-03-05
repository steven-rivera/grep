from dataclasses import dataclass
from abc import ABC, abstractmethod
from collections import deque


@dataclass
class MatchState:
    pos: int  # Current position in the string
    captures: dict[
        int, tuple[int, int]
    ]  # Keys are group ID's and values are the start and end index of captured group


class Node(ABC):
    @abstractmethod
    def match(self, s: str, state: MatchState) -> list[MatchState]:
        pass


class Empty(Node):
    def __str__(self) -> str:
        return "Empty()"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        return [MatchState(pos=state.pos, captures=state.captures.copy())]


class Literal(Node):
    def __init__(self, literal: str):
        self.literal = literal

    def __str__(self) -> str:
        return f"Literal('{self.literal}')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]
        if c == self.literal:
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        return []


class Dot(Node):
    def __str__(self) -> str:
        return "Dot('.')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]
        if c != "\n":
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        return []


class StartAnchor(Node):
    def __str__(self) -> str:
        return "StartAnchor('^')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos == 0:
            return [state]
        return []


class EndAnchor(Node):
    def __str__(self) -> str:
        return "EndAnchor('$')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos == len(s):
            return [state]
        return []


class CharacterClass(Node):
    def __init__(self, chars: set[str], complement: bool):
        self.chars = chars
        self.complement = complement

    def __str__(self) -> str:
        return (
            f"CharacterClass('[{'^' if self.complement else ''}{''.join(self.chars)}]')"
        )

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]

        if c in self.chars:
            if not self.complement:
                return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        elif self.complement and c.isalpha():
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]

        return []


class MetaSequence(Node):
    @staticmethod
    def is_digit(c: str) -> bool:
        return c.isdecimal()

    @staticmethod
    def is_word_char(c: str) -> bool:
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9") or (c == "_")

    @staticmethod
    def is_space(c: str) -> bool:
        return c.isspace()

    registry = {
        "d": is_digit,
        "w": is_word_char,
        "s": is_space,
    }

    def __init__(self, metaSequence: str):
        self.metaSequence = metaSequence

    def __str__(self) -> str:
        return f"MetaSequence('\\{self.metaSequence}')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]
        test = MetaSequence.registry[self.metaSequence]

        if test(c):
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        return []


class Star(Node):
    def __init__(self, node: Node):
        self.node = node

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = [state]
        queue = deque([state])
        visited = set([state.pos])

        while len(queue) != 0:
            curr_state = queue.popleft()

            for next_state in self.node.match(s, curr_state):
                if next_state.pos in visited:
                    continue

                visited.add(next_state.pos)
                queue.append(next_state)
                results.append(next_state)

        # Greedy (longest matches at beginning of array)
        return list(sorted(results, key=lambda match: match.pos, reverse=True))


class Plus(Node):
    def __init__(self, node: Node):
        self.node = node

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = []
        queue = deque([state])
        visited = set()

        while len(queue) != 0:
            curr_state = queue.popleft()

            for next_state in self.node.match(s, curr_state):
                if next_state.pos in visited:
                    continue

                visited.add(next_state.pos)
                queue.append(next_state)
                results.append(next_state)

        # Greedy (longest matches at beginning of array)
        return list(sorted(results, key=lambda match: match.pos, reverse=True))


class Optional(Node):
    def __init__(self, node: Node):
        self.node = node

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = []
        visited = set()

        for next_state in self.node.match(s, state):
            if next_state.pos in visited:
                continue

            visited.add(next_state.pos)
            results.append(next_state)

        if state.pos not in visited:
            results.append(state)

        return list(sorted(results, key=lambda match: match.pos, reverse=True))


class Range(Node):
    def __init__(self, node: Node, min: int, max: int):
        self.node = node
        self.min = min
        self.max = max

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        frontier = [state]

        for _ in range(self.min):
            new_frontier = []
            for curr_state in frontier:
                new_frontier.extend(self.node.match(s, curr_state))

            if len(new_frontier) == 0:
                return []

            frontier = new_frontier

        results = frontier

        # Case {n}
        if self.min == self.max:
            return list(sorted(results, key=lambda match: match.pos, reverse=True))

        # Case {n,m}
        remaining = self.max - self.min
        for _ in range(remaining):
            new_frontier = []
            for curr_state in frontier:
                new_frontier.extend(self.node.match(s, curr_state))

            if len(new_frontier) == 0:
                break

            results.extend(new_frontier)
            frontier = new_frontier

        return list(sorted(results, key=lambda match: match.pos, reverse=True))


class Alternation(Node):
    def __init__(self, options: list[Node]):
        self.options = options

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = []
        for option in self.options:
            results.extend(option.match(s, state))
        return results


class Group(Node):
    def __init__(
        self,
        group_id: int,
        node: Node,
    ):
        self.group_id = group_id
        self.node = node

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        start = state.pos
        results = []

        for new_state in self.node.match(s, state):
            new_captures = {**new_state.captures, self.group_id: (start, new_state.pos)}

            results.append(MatchState(pos=new_state.pos, captures=new_captures))

        return results


class BackReference(Node):
    def __init__(self, group_id: int):
        self.group_id = group_id

    def __str__(self) -> str:
        return f"BackReference({self.group_id})"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if self.group_id not in state.captures:
            return []

        start, end = state.captures[self.group_id]
        text = s[start:end]

        if s.startswith(text, state.pos):
            return [
                MatchState(pos=state.pos + len(text), captures=state.captures.copy())
            ]

        return []


class Sequence(Node):
    def __init__(self, nodes: list[Node]):
        self.nodes = nodes

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        queue = deque([(0, state)])
        results = []

        while len(queue) != 0:
            index, curr_state = queue.popleft()

            # If we've matched all nodes
            if index == len(self.nodes):
                results.append(curr_state)
                continue

            node = self.nodes[index]

            for next_state in node.match(s, curr_state):
                queue.append((index + 1, next_state))

        return results


def stringifyNode(node: Node, level=0) -> str:
    indent = "    " * level

    match node:
        case Sequence(nodes=children) | Alternation(options=children):
            label = type(node).__name__
            body = ",\n".join(stringifyNode(c, level + 1) for c in children)
            return f"{indent}{label}([\n{body}\n{indent}])"

        case Star(node=child) | Plus(node=child) | Optional(node=child):
            label = type(node).__name__
            return f"{indent}{label}(\n{stringifyNode(child, level + 1)}\n{indent})"

        case Group(node=child, group_id=group):
            return f"{indent}Group(group={group}\n{stringifyNode(child, level + 1)}\n{indent})"

        case Range(node=child, min=min, max=max):
            return f"{indent}Range(min={min}, max={max}\n{stringifyNode(child, level + 1)}\n{indent})"

        case _:
            return f"{indent}{node}"


@dataclass
class Match:
    match: str
    span: tuple[int, int]
    captures: dict[int, tuple[int, int]]

    def start(self) -> int:
        return self.span[0]

    def end(self) -> int:
        return self.span[1]


class Pattern:
    def __init__(self, pattern: str, numGroups: int, ast: Node):
        self.pattern = pattern
        self.numGroups = numGroups
        self.ast = ast

    def search(self, s: str) -> Match | None:
        i = 0
        while i < len(s):
            matchStates = self.ast.match(s, MatchState(i, {}))
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
        matchStates = self.ast.match(s, MatchState(0, {}))
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
            matchStates = self.ast.match(s, MatchState(i, {}))
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



class InvalidPattern(Exception):
    pass


class Parser:
    meta_characters = {
        ".",
        "^",
        "$",
        "*",
        "+",
        "?",
        "{",
        "}",
        "(",
        ")",
        "[",
        "]",
        "\\",
        "|",
    }

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self.i = 0
        self.curr_group_id = 1
        self.ast = None

    def parse(self) -> tuple[Node, int]:
        if self.ast is None:
            self.ast = self._parse_expression()
        return self.ast, self.curr_group_id - 1

    def _peek(self) -> str:
        if self.i >= len(self.pattern):
            return ""
        return self.pattern[self.i]

    def _consume(self, expected=None) -> str:
        if self.i >= len(self.pattern):
            raise IndexError("At end of pattern")

        c = self.pattern[self.i]

        if expected is not None and c != expected:
            raise ValueError(f"Expected '{expected}' got '{c}'")

        self.i += 1
        return c

    def _parse_expression(self) -> Node:
        left = self._parse_sequence()

        if self._peek() == "|":
            options = [left]

            while self._peek() == "|":
                self._consume("|")
                options.append(self._parse_sequence())

            return Alternation(options)

        return left

    def _parse_sequence(self) -> Node:
        nodes = []

        while self.i < len(self.pattern) and self._peek() not in "|)":
            nodes.append(self._parse_repetition())

        if len(nodes) == 0:
            return Empty()

        if len(nodes) == 1:
            return nodes[0]

        return Sequence(nodes)

    def _parse_repetition(self) -> Node:
        node = self._parse_atom()

        c = self._peek()

        if c == "*":
            self._consume()
            return Star(node)
        if c == "+":
            self._consume()
            return Plus(node)
        if c == "?":
            self._consume()
            return Optional(node)
        if c == "{":
            return self._parse_range(node)

        return node

    def _parse_atom(self) -> Node:
        c = self._peek()

        if c == "(":
            return self._parse_group()
        if c == "[":
            return self._parse_charclass()
        if c == "\\":
            return self._parse_backslash()
        if c == ".":
            self._consume()
            return Dot()
        if c == "^":
            self._consume()
            return StartAnchor()
        if c == "$":
            self._consume()
            return EndAnchor()

        if c == ")":
            raise InvalidPattern("')': Unmatched group")

        self._consume()
        return Literal(c)

    def _parse_backslash(self) -> Node:
        self._consume("\\")

        if self.i == len(self.pattern):
            raise InvalidPattern("'': Pattern cannot end with trailing backslash")

        c = self._peek()

        if c in MetaSequence.registry:
            self._consume()
            return MetaSequence(c)

        if c in Parser.meta_characters:
            self._consume()
            return Literal(c)

        if c.isdecimal():
            group = self._consume()

            while self._peek().isdecimal():
                group += self._consume()

            group = int(group)
            if group >= self.curr_group_id:
                raise InvalidPattern(f"'{group}': Invalid group reference")

            return BackReference(group_id=group)

        raise InvalidPattern(f"'\\{c}': This token has no special meaning")

    def _parse_range(self, node: Node) -> Node:
        self._consume("{")

        min, max = "", ""
        seenMax = False

        while self.i < len(self.pattern) and ((c := self._peek()) != "}"):
            if c == ",":
                seenMax = True
                self._consume(",")
                break

            if not c.isdecimal():
                raise InvalidPattern(f"'{c}': Invalid character in range quantifier")

            min += c
            self._consume()

        while self.i < len(self.pattern) and ((c := self._peek()) != "}"):
            if not c.isdecimal():
                raise InvalidPattern(f"'{c}': Invalid character in range quantifier")

            max += c
            self._consume()

        if (c := self._peek()) != "}":
            raise InvalidPattern("Missing closing '}'")
        self._consume("}")

        # Case {n}
        if not seenMax:
            return Range(node, int(min), int(min))

        # Case {n,}
        if max == "":
            return Sequence(
                [
                    Range(node, int(min), int(min)),
                    Star(node),
                ]
            )

        # Case {n,m}
        if int(min) > int(max):
            raise InvalidPattern(f"'{min} > {max}': Range quantifier is out of order")
        return Range(node, int(min), int(max))

    def _parse_group(self) -> Node:
        self._consume("(")
        group_id = self.curr_group_id
        self.curr_group_id += 1

        node = self._parse_expression()

        if self._peek() != ")":
            raise InvalidPattern("')': Unmatched parenthesis")

        self._consume(")")
        return Group(group_id, node)

    def _parse_charclass(self) -> Node:
        self._consume("[")

        complement = False
        if self._peek() == "^":
            complement = True
            self._consume()

        chars = []

        while self.i < len(self.pattern) and self._peek() != "]":
            c = self._peek()

            if c != "-" or len(chars) == 0:
                chars.append(c)
                self._consume()
                continue

            c = self._consume("-")

            if self.i >= len(self.pattern):
                raise InvalidPattern("']': Unmatched bracket")

            if self._peek() == "]":
                chars.append(c)
                self._consume()
                continue

            start = chars.pop()
            end = self._consume()

            if ord(start) > ord(end):
                raise InvalidPattern(f"'{start}-{end}': Invalid character range")

            chars.extend([chr(i) for i in range(ord(start), ord(end) + 1)])

        if self._peek() != "]":
            raise InvalidPattern("']': Unmatched bracket")

        self._consume("]")

        return CharacterClass(chars=set(chars), complement=complement)



def compile(pattern: str) -> Pattern:
    parser = Parser(pattern)
    ast, numGroups = parser.parse()

    return Pattern(pattern=pattern, ast=ast, numGroups=numGroups)