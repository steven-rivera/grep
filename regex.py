from enum import Enum, auto

class InvalidPattern(Exception):
    pass


class TokenType(Enum):
    CHAR = auto()  # 'a'
    ANCHOR_START = auto()  # '^'
    ANCHOR_END = auto()  # '$'
    PREDEFINED_CLASS = auto()  # '\d'
    CHARACTER_CLASS = auto()  # [...]

    QUANTIFIER_STAR = auto()  # '*'
    QUANTIFIER_PLUS = auto()  # '+'
    QUANTIFIER_OPTIONAL = auto()  # '?'
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
        self.tokens: list[Token] = self._compileTokens()
        self.capturedGroups = [Captured() for _ in range(RE.MAX_CAPTURE_GROUPS)]

    def _compileTokens(self):
        self._currGroupNum = 1

        def _compileTokensHelper(subPattern: str) -> list[Token]:
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
                            if int(c) >= self._currGroupNum:
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
                        numOpeningParen, seenClosingParen = 1, False
                        groupTokens, groupNum, groupPattern = [], self._currGroupNum, ""
                        self._currGroupNum += 1

                        while i < len(subPattern):
                            if subPattern[i] == ")" and numOpeningParen == 1:
                                if groupPattern != "":
                                    groupTokens.append(_compileTokensHelper(groupPattern))
                                seenClosingParen = True
                                break
                            elif subPattern[i] == "|" and numOpeningParen == 1:
                                groupTokens.append(_compileTokensHelper(groupPattern))
                                groupPattern = ""
                            else:
                                if subPattern[i] == "(":
                                    numOpeningParen += 1
                                if subPattern[i] == ")":
                                    numOpeningParen -= 1
                                groupPattern += subPattern[i]
                            i += 1
                        if not seenClosingParen:
                            raise InvalidPattern("No closing brace ')'")
                        
                        tokens.append(
                            TokenGroup(
                                type=TokenType.GROUP,
                                group=groupTokens,
                                groupNum=groupNum,
                            )
                        )
                        
                    case _:
                        tokens.append(TokenChar(type=TokenType.CHAR, char=c))
                i += 1

            return tokens

        return _compileTokensHelper(self.pattern)

    def matchPattern(self, text: str) -> bool:
        textIdx = 0
        while True:
            foundMatch, _ = self.matchHere(
                text, textIdx=textIdx, tokens=self.tokens)
            if foundMatch:
                return True
            # Condition checked after to permit zero-length matches
            if textIdx >= len(text):
                break
            textIdx += 1
        return False

    def matchHere(self, text: str, textIdx: int, tokens: list[Token]) -> tuple[bool, int]:
        potentialMatch = [(textIdx, 0)]

        while len(potentialMatch) != 0:
            currTextIdx, currTokenIdx = potentialMatch.pop()

            while currTokenIdx < len(tokens):
                currToken = tokens[currTokenIdx]

                if currToken.type == TokenType.QUANTIFIER_PLUS:
                    textEnd = len(text)
                    while currTextIdx != textEnd:
                        containsPrev, endIdx = self.matchHere(text, currTextIdx, [currToken.prev])
                        if not containsPrev:
                            break
                        
                        potentialMatch.append((endIdx, currTokenIdx+1))
                        currTextIdx = endIdx
                    break

                if currToken.type == TokenType.GROUP:
                    for subTokens in currToken.group:
                        foundMatch, endIdx = self.matchHere(text, currTextIdx, subTokens)
                        if not foundMatch:
                            continue
                        captured = self.capturedGroups[currToken.groupNum - 1]
                        captured.start, captured.end = currTextIdx, endIdx
                        
                        potentialMatch.append((endIdx, currTokenIdx+1))
                    break

                if currToken.type == TokenType.QUANTIFIER_OPTIONAL:
                    potentialMatch.append((currTextIdx, currTokenIdx+1))
                    containsPrev, endIdx = self.matchHere(text, currTextIdx, [currToken.prev])
                    if containsPrev:
                        potentialMatch.append((endIdx, currTokenIdx+1)) 
                    break

                if currToken.type == TokenType.BACKREFERENCE:
                    captured = self.capturedGroups[currToken.groupNum - 1]
                    subTokens = [TokenChar(type=TokenType.CHAR, char=c) for c in text[captured.start : captured.end]]

                    foundMatch, endIdx = self.matchHere(text, currTextIdx, subTokens)
                    if foundMatch:
                        potentialMatch.append((endIdx, currTokenIdx+1)) 
                    break

                foundMatch, endIdx = currToken.match(text, currTextIdx)
                if not foundMatch:
                    break
                
                currTextIdx = endIdx
                currTokenIdx += 1

            if currTokenIdx == len(tokens):
                return True, currTextIdx

        return False, -1