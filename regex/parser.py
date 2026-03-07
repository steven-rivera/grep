from .nodes import (
    Node,
    Empty,
    Literal,
    Dot,
    StartAnchor,
    EndAnchor,
    CharacterClass,
    MetaSequence,
    Star,
    Plus,
    Optional,
    Range,
    Alternation,
    Group,
    BackReference,
    Sequence,
)


class InvalidPattern(Exception):
    pass


class Parser:
    META_CHARS = {
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

    QUANTIFIERS = {
        "*": Star,
        "+": Plus,
        "?": Optional,
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

        if c in Parser.QUANTIFIERS:
            self._consume(c)

            is_lazy = False
            if self._peek() == "?":
                self._consume("?")
                is_lazy = True

            return Parser.QUANTIFIERS[c](node, is_lazy=is_lazy)

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

        if c in Parser.META_CHARS:
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
        is_lazy = False
        if self._peek() == "?":
            self._consume("?")
            is_lazy = True

        # Case {n}
        if not seenMax:
            return Range(node, int(min), int(min), is_lazy=is_lazy)

        # Case {n,}
        if max == "":
            return Sequence(
                [
                    Range(node, int(min), int(min), is_lazy=is_lazy),
                    Star(node, is_lazy=is_lazy),
                ]
            )

        # Case {n,m}
        if int(min) > int(max):
            raise InvalidPattern(f"'{min} > {max}': Range quantifier is out of order")
        return Range(node, int(min), int(max), is_lazy=is_lazy)

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
