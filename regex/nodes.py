from abc import ABC, abstractmethod
from collections import deque
from .match import MatchState


class Node(ABC):
    @abstractmethod
    def match(self, s: str, state: MatchState) -> list[MatchState]:
        pass


class Empty(Node):
    def __str__(self) -> str:
        return "Empty()"

    def __eq__(self, other) -> bool:
        return isinstance(other, Empty)

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        return [MatchState(pos=state.pos, captures=state.captures.copy())]


class Literal(Node):
    def __init__(self, literal: str):
        self.literal = literal

    def __eq__(self, other) -> bool:
        if isinstance(other, Literal):
            return other.literal == self.literal
        return False

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
    def __eq__(self, other) -> bool:
        return isinstance(other, Dot)

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
    def __eq__(self, other) -> bool:
        return isinstance(other, StartAnchor)

    def __str__(self) -> str:
        return "StartAnchor('^')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos == 0:
            return [state]
        return []


class EndAnchor(Node):
    def __eq__(self, other) -> bool:
        return isinstance(other, EndAnchor)

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

    def __eq__(self, other) -> bool:
        if isinstance(other, CharacterClass):
            return other.chars == self.chars and other.complement == self.complement
        return False

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
                return [
                    MatchState(
                        pos=state.pos + 1,
                        captures=state.captures.copy(),
                    )
                ]
        elif self.complement and c.isalpha():
            return [
                MatchState(
                    pos=state.pos + 1,
                    captures=state.captures.copy(),
                )
            ]

        return []


class MetaSequence(Node):
    @staticmethod
    def is_word_char(c: str) -> bool:
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9") or (c == "_")

    def match_digit(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]

        if c.isdecimal():
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        return []

    def match_word_char(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]

        if MetaSequence.is_word_char(c):
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        return []

    def match_space(self, s: str, state: MatchState) -> list[MatchState]:
        if state.pos >= len(s):
            return []

        c = s[state.pos]

        if c.isspace():
            return [MatchState(pos=state.pos + 1, captures=state.captures.copy())]
        return []

    def match_word_boundary(self, s: str, state: MatchState) -> list[MatchState]:
        # Handle match at end of string
        if state.pos >= len(s):
            prev_c = s[state.pos - 1]

            if MetaSequence.is_word_char(prev_c):
                return [MatchState(pos=state.pos, captures=state.captures.copy())]
            return []

        # Handle match at beginning of string
        if state.pos == 0:
            c = s[state.pos]

            if MetaSequence.is_word_char(c):
                return [MatchState(pos=state.pos, captures=state.captures.copy())]
            return []

        prev_c = s[state.pos - 1]
        c = s[state.pos]

        if MetaSequence.is_word_char(prev_c) ^ MetaSequence.is_word_char(c):
            return [MatchState(pos=state.pos, captures=state.captures.copy())]
        return []

    registry = {
        "d": match_digit,
        "w": match_word_char,
        "s": match_space,
        "b": match_word_boundary,
    }

    def __init__(self, metaSequence: str):
        self.metaSequence = metaSequence

    def __eq__(self, other) -> bool:
        if isinstance(other, MetaSequence):
            return other.metaSequence == self.metaSequence
        return False

    def __str__(self) -> str:
        return f"MetaSequence('\\{self.metaSequence}')"

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        matcher = MetaSequence.registry[self.metaSequence]
        return matcher(self, s, state)


class Star(Node):
    def __init__(self, node: Node, is_lazy: bool = False):
        self.node = node
        self.is_lazy = is_lazy

    def __eq__(self, other) -> bool:
        if isinstance(other, Star):
            return other.node == self.node and other.is_lazy == self.is_lazy
        return False

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = [state]
        visited = set([state])
        queue = deque([state])
        

        while len(queue) != 0:
            curr_state = queue.popleft()

            for next_state in self.node.match(s, curr_state):
                if next_state in visited:
                    continue

                visited.add(next_state)
                queue.append(next_state)
                results.append(next_state)
        
        if self.is_lazy:
            return list(reversed(results))
        
        return results


class Plus(Node):
    def __init__(self, node: Node, is_lazy: bool = False):
        self.node = node
        self.is_lazy = is_lazy

    def __eq__(self, other) -> bool:
        if isinstance(other, Plus):
            return other.node == self.node and other.is_lazy == self.is_lazy
        return False

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = []
        visited = set()
        queue = deque([state])
        
        while len(queue) != 0:
            curr_state = queue.popleft()

            for next_state in self.node.match(s, curr_state):
                if next_state in visited:
                    continue

                visited.add(next_state)
                queue.append(next_state)
                results.append(next_state)

        if self.is_lazy:
            return list(reversed(results))
        
        return results


class Optional(Node):
    def __init__(self, node: Node, is_lazy: bool = False):
        self.node = node
        self.is_lazy = is_lazy

    def __eq__(self, other) -> bool:
        if isinstance(other, Optional):
            return other.node == self.node and other.is_lazy == self.is_lazy
        return False

    def match(self, s: str, state: MatchState) -> list[MatchState]:
        results = [state]
        visited = set([state])

        for next_state in self.node.match(s, state):
            if next_state in visited:
                continue

            visited.add(next_state)
            results.append(next_state)

        if self.is_lazy:
            return list(reversed(results))
        
        return results


class Range(Node):
    def __init__(self, node: Node, min: int, max: int, is_lazy: bool = False):
        self.node = node
        self.min = min
        self.max = max
        self.is_lazy = is_lazy

    def __eq__(self, other) -> bool:
        if isinstance(other, Range):
            return (
                other.node == self.node
                and other.min == self.min
                and other.max == self.max
                and other.is_lazy == self.is_lazy
            )
        return False

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

        # Only runs for {n,m}
        for _ in range(self.max - self.min):
            new_frontier = []
            for curr_state in frontier:
                new_frontier.extend(self.node.match(s, curr_state))

            if len(new_frontier) == 0:
                break

            results.extend(new_frontier)
            frontier = new_frontier

        if self.is_lazy:
            return list(reversed(results))
        return results



class Alternation(Node):
    def __init__(self, options: list[Node]):
        self.options = options

    def __eq__(self, other) -> bool:
        if isinstance(other, Alternation):
            return other.options == self.options
        return False

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

    def __eq__(self, other) -> bool:
        if isinstance(other, Group):
            return other.group_id == self.group_id and other.node == self.node
        return False

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

    def __eq__(self, other) -> bool:
        if isinstance(other, BackReference):
            return other.group_id == self.group_id
        return False

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

    def __eq__(self, other) -> bool:
        if isinstance(other, Sequence):
            return other.nodes == self.nodes
        return False

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


def stringify_node(node: Node, level=0) -> str:
    indent = "    " * level

    match node:
        case Sequence(nodes=children) | Alternation(options=children):
            label = type(node).__name__
            body = ",\n".join(stringify_node(c, level + 1) for c in children)
            return f"{indent}{label}([\n{body}\n{indent}])"

        case Star(node=child) | Plus(node=child) | Optional(node=child):
            label = type(node).__name__
            return f"{indent}{label}(\n{stringify_node(child, level + 1)}\n{indent})"

        case Group(node=child, group_id=group):
            return f"{indent}Group(group={group}\n{stringify_node(child, level + 1)}\n{indent})"

        case Range(node=child, min=min, max=max):
            return f"{indent}Range(min={min}, max={max}\n{stringify_node(child, level + 1)}\n{indent})"

        case _:
            return f"{indent}{node}"
