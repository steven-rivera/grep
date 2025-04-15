from enum import Enum, auto

class InvalidPattern(Exception):
    pass


class TokenType(Enum):
    CHAR = auto()  # 'a'

    QUANTIFIER_STAR = auto()  # '*'
    QUANTIFIER_PLUS = auto()  # '+'
    QUANTIFIER_OPTIONAL = auto()  # '?'

    ANCHOR_START = auto()  # '^'
    ANCHOR_END = auto()  # '$'

    PREDEFINED_CLASS = auto()  # '\d'
    CHARACTER_CLASS = auto()  # [...]

    GROUP = auto()  # (...)
    BACKREFERENCE = auto()  # \1


class Token:
    def __init__(self, type: TokenType):
        self.type = type


class TokenChar(Token):
    def __init__(self, type: TokenType, char: str):
        super().__init__(type)
        self.char = char

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx < len(text):
            char = text[textIdx]
            if char == self.char or self.char == ".":
                return True, textIdx + 1
        return False, -1


class TokenStar(Token):
    def __init__(self, type: TokenType, prev: Token):
        super().__init__(type)
        self.prev = prev


class TokenPlus(Token):
    def __init__(self, type: TokenType, prev: Token):
        super().__init__(type)
        self.prev = prev
    

class TokenOptional(Token):
    def __init__(self, type: TokenType, prev: Token):
        super().__init__(type)
        self.prev = prev

class TokenStart(Token):
    def __init__(self, type: TokenType):
        super().__init__(type)

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx == 0:
            return True, 0
        return False, -1

class TokenEnd(Token):
    def __init__(self, type: TokenType):
        super().__init__(type)

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx == len(text):
            return True, len(text)
        return False, -1

class TokenPredifinedClass(Token):
    def __init__(self, type: TokenType, char: str, negated: bool):
        super().__init__(type)
        self.char = char
        self.negated = negated

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx < len(text):
            match self.char:
                case "d":
                    if text[textIdx].isdigit():
                        return True, textIdx + 1
                case "w":
                    if text[textIdx].isalpha():
                        return True, textIdx + 1
                case "\\":
                    if text[textIdx] == "\\":
                        return True, textIdx + 1
        return False, -1

class TokenCharacterClass(Token):
    def __init__(self, type: TokenType, chars: set[str], negated: bool):
        super().__init__(type)
        self.chars = chars
        self.negated = negated

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx < len(text):
            if self.negated and text[textIdx] not in self.chars and text[textIdx].isalpha():
                return True, textIdx + 1

            if not self.negated and text[textIdx] in self.chars:
                return True, textIdx + 1

        return False , -1


class TokenGroup(Token):
    def __init__(self, type: TokenType, group: list[list[Token]], groupNum: int):
        super().__init__(type)
        self.group = group
        self.groupNum = groupNum


class TokenBackreference(Token):
    def __init__(self, type: TokenType, groupNum: int):
        super().__init__(type)
        self.groupNum = groupNum


class Match:
    def __init__(self, start: int = -1, end: int = -1):
        self.start = start
        self.end = end

    def string(self, text: str) -> str:
        if self.start < 0 or self.end < 0:
            return ""
        return text[self.start : self.end]


class Captured(Match):
    def __init__(self):
        super().__init__()


class RE:
    MAX_CAPTURE_GROUPS = 10

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.tokens: list[Token] = self.compileTokens()
        self.capturedGroups = [Captured() for _ in range(RE.MAX_CAPTURE_GROUPS)]

    def compileTokens(self):
        self._currGroupNum = 0

        def _compileTokens(subPattern: str) -> list[Token]:
            tokens, i = [], 0
            while i < len(subPattern):
                c = subPattern[i]

                match c:
                    case "*":
                        if len(tokens) == 0:
                            raise InvalidPattern(
                                "No previous pattern to repeat zero or more times"
                            )
                        prevToken = tokens.pop()
                        tokens.append(
                            TokenStar(type=TokenType.QUANTIFIER_STAR, prev=prevToken)
                        )

                    case "+":
                        if len(tokens) == 0:
                            raise InvalidPattern(
                                "No previous pattern to repeat one or more times"
                            )
                        prevToken = tokens.pop()
                        tokens.append(
                            TokenPlus(type=TokenType.QUANTIFIER_PLUS, prev=prevToken)
                        )

                    case "?":
                        if len(tokens) == 0:
                            raise InvalidPattern("No previous pattern to make optional")
                        prevToken = tokens.pop()

                        tokens.append(
                            TokenOptional(
                                type=TokenType.QUANTIFIER_OPTIONAL, prev=prevToken
                            )
                        )

                    case "^":
                        if i != 0:
                            raise InvalidPattern(
                                "'^' must be first character in pattern"
                            )

                        tokens.append(TokenStart(type=TokenType.ANCHOR_START))

                    case "$":
                        if i != len(subPattern) - 1:
                            raise InvalidPattern(
                                "'$' must be last character in pattern"
                            )

                        tokens.append(TokenEnd(type=TokenType.ANCHOR_END))

                    case "\\":
                        i += 1
                        if i >= len(subPattern):
                            raise InvalidPattern("Expected character class after '\\'")

                        c = subPattern[i]
                        if c.isdigit():
                            if int(c) > self._currGroupNum:
                                raise InvalidPattern(
                                    f"Invalid capture group number '{c}'"
                                )
                            tokens.append(
                                TokenBackreference(
                                    type=TokenType.BACKREFERENCE, groupNum=int(c)
                                )
                            )
                        else:
                            if c not in "dw\\":
                                raise InvalidPattern(f"Invalid character class '\\{c}'")
                            tokens.append(
                                TokenPredifinedClass(
                                    type=TokenType.PREDEFINED_CLASS,
                                    char=c,
                                    negated=False,
                                )
                            )

                    case "[":
                        i += 1
                        charSet, negated, seenClosingBracket = set(), False, False

                        if subPattern[i] == "^":
                            negated = True
                            i += 1

                        while i < len(subPattern):
                            if subPattern[i] == "]":
                                seenClosingBracket = True
                                break

                            charSet.add(subPattern[i])
                            i += 1

                        if not seenClosingBracket:
                            raise InvalidPattern("No closing bracket ']'")

                        tokens.append(
                            TokenCharacterClass(
                                type=TokenType.CHARACTER_CLASS,
                                chars=charSet,
                                negated=negated,
                            )
                        )

                    case "(":
                        i += 1
                        self._currGroupNum += 1

                        openingParen, seenClosingParen = 1, False
                        groupTokens, groupPattern = [], ""

                        tokens.append(
                            TokenGroup(
                                type=TokenType.GROUP,
                                group=groupTokens,
                                groupNum=self._currGroupNum,
                            )
                        )

                        while i < len(subPattern):
                            if subPattern[i] == ")" and openingParen == 1:
                                if groupPattern != "":
                                    groupTokens.append(_compileTokens(groupPattern))
                                seenClosingParen = True
                                break
                            elif subPattern[i] == "|" and openingParen == 1:
                                groupTokens.append(_compileTokens(groupPattern))
                                groupPattern = ""
                            else:
                                if subPattern[i] == "(":
                                    openingParen += 1
                                if subPattern[i] == ")":
                                    openingParen -= 1
                                groupPattern += subPattern[i]
                            i += 1

                        if not seenClosingParen:
                            raise InvalidPattern("No closing brace ')'")
                    case _:
                        tokens.append(TokenChar(type=TokenType.CHAR, char=c))
                i += 1

            return tokens

        return _compileTokens(self.pattern)

    def matchPattern(self, text: str) -> bool:
        if self.tokens[0].type == TokenType.ANCHOR_START:
            foundMatch, _ = self._matchHere(
                text, textIdx=0, tokens=self.tokens, tokenIdx=1
            )
            return foundMatch

        textIdx = 0
        while True:
            foundMatch, _ = self._matchHere(
                text, textIdx=textIdx, tokens=self.tokens, tokenIdx=0
            )
            if foundMatch:
                return True

            # Condition checked after to permit zero-length matches
            if textIdx >= len(text):
                break

            textIdx += 1

        return False

    def _matchHere(
        self, text: str, textIdx: int, tokens: list[Token], tokenIdx: int
    ) -> tuple[bool, int]:
        textEnd, tokenEnd = len(text), len(tokens)

        # Base case: reached end of pattern
        if tokenIdx == tokenEnd:
            return (True, textIdx)

        # if textIdx == textEnd:
        #     return False

        currToken = tokens[tokenIdx]

        if currToken.type == TokenType.ANCHOR_END:
            if textIdx == textEnd:
                return True, textIdx
            return False, -1

        if currToken.type == TokenType.QUANTIFIER_OPTIONAL:
            foundMatch, endIdx = self._matchHere(text, textIdx, tokens, tokenIdx + 1)
            if foundMatch:
                return foundMatch, endIdx

            foundPrev, endIdx = self._matchHere(text, textIdx, [currToken.prev], 0)
            if foundPrev:
                return self._matchHere(text, endIdx, tokens, tokenIdx + 1)

            return False, -1

        if currToken.type == TokenType.QUANTIFIER_PLUS and textIdx != textEnd:
            return self._matchPlus(currToken.prev, text, textIdx, tokens, tokenIdx + 1)

        if currToken.type == TokenType.PREDEFINED_CLASS and textIdx != textEnd:
            match currToken.char:
                case "d":
                    if text[textIdx].isdigit():
                        return self._matchHere(text, textIdx + 1, tokens, tokenIdx + 1)
                case "w":
                    if text[textIdx].isalpha():
                        return self._matchHere(text, textIdx + 1, tokens, tokenIdx + 1)
                case "\\":
                    if text[textIdx] == "\\":
                        return self._matchHere(text, textIdx + 1, tokens, tokenIdx + 1)

        if currToken.type == TokenType.CHARACTER_CLASS and textIdx != textEnd:
            if (
                currToken.negated
                and text[textIdx] not in currToken.chars
                and text[textIdx].isalpha()
            ):
                return self._matchHere(text, textIdx + 1, tokens, tokenIdx + 1)

            if not currToken.negated and text[textIdx] in currToken.chars:
                return self._matchHere(text, textIdx + 1, tokens, tokenIdx + 1)

        if currToken.type == TokenType.GROUP:
            for subTokens in currToken.group:
                foundMatch, endIdx = self._matchHere(text, textIdx, subTokens, 0)
                if not foundMatch:
                    continue

                captured = self.capturedGroups[currToken.groupNum - 1]
                captured.start, captured.end = textIdx, endIdx

                foundMatch, endIdx = self._matchHere(text, endIdx, tokens, tokenIdx + 1)
                if foundMatch:
                    return foundMatch, endIdx

            return False, -1

        if currToken.type == TokenType.BACKREFERENCE:
            captured = self.capturedGroups[currToken.groupNum - 1]
            subTokens = [
                TokenChar(type=TokenType.CHAR, char=c)
                for c in text[captured.start : captured.end]
            ]

            foundMatch, endIdx = self._matchHere(text, textIdx, subTokens, 0)
            if not foundMatch:
                return False, -1

            return self._matchHere(text, endIdx, tokens, tokenIdx + 1)

        if (
            currToken.type == TokenType.CHAR
            and textIdx != textEnd
            and (text[textIdx] == currToken.char or currToken.char == ".")
        ):
            return self._matchHere(text, textIdx + 1, tokens, tokenIdx + 1)

        return False, -1

    def _matchPlus(
        self,
        prevToken: Token,
        text: str,
        textIdx: int,
        tokens: list[Token],
        tokenIdx: str,
    ) -> tuple[bool, int]:
        textEnd = len(text)
        prevTextIdx = textIdx
        matchLengths = []

        while textIdx != textEnd:
            containsPrev, endIdx = self._matchHere(text, textIdx, [prevToken], 0)
            if not containsPrev:
                break

            matchLengths.append(endIdx - textIdx)
            textIdx = endIdx

        while textIdx > prevTextIdx:
            foundMatch, endIdx = self._matchHere(text, textIdx, tokens, tokenIdx)
            if foundMatch:
                return True, endIdx
            textIdx -= matchLengths.pop()

        return False, -1

