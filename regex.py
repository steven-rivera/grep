from enum import Enum, auto

class InvalidPattern(Exception):
    pass


class TokenType(Enum):
    # Base Tokens implement their own 
    # matching functions 
    CHAR                = auto()  # a
    START               = auto()  # ^
    END                 = auto()  # $
    PREDEFINED_CLASS    = auto()  # \d
    CHARACTER_CLASS     = auto()  # [abc] or [^abc]
    
    # Complex Tokens consist of other
    # nase tokens or complex tokens
    STAR                = auto()  # *
    PLUS                = auto()  # +
    OPTIONAL            = auto()  # ?
    GROUP               = auto()  # (abc) or (abc|def)
    BACKREFERENCE       = auto()  # \1


class Token:
    def __init__(self, type: TokenType):
        self.type = type


class TokenChar(Token):
    def __init__(self, char: str):
        super().__init__(TokenType.CHAR)
        self.char = char

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx < len(text):
            char = text[textIdx]
            if char == self.char or self.char == ".":
                return True, textIdx + 1
        return False, -1

class TokenStart(Token):
    def __init__(self):
        super().__init__(TokenType.START)

    def match(self, _: str, textIdx: int) -> tuple[bool, int]:
        if textIdx == 0:
            return True, 0
        return False, -1

class TokenEnd(Token):
    def __init__(self):
        super().__init__(TokenType.END)

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx == len(text):
            return True, textIdx
        return False, -1

class TokenPredifinedClass(Token):
    def __init__(self, char: str):
        super().__init__(TokenType.PREDEFINED_CLASS)
        self.char = char

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
    def __init__(self, chars: set[str], negated: bool):
        super().__init__(TokenType.CHARACTER_CLASS)
        self.chars = chars
        self.negated = negated

    def match(self, text: str, textIdx: int) -> tuple[bool, int]:
        if textIdx < len(text):
            if (
                self.negated
                and text[textIdx] not in self.chars
                and text[textIdx].isalpha()
            ):
                return True, textIdx + 1

            if not self.negated and text[textIdx] in self.chars:
                return True, textIdx + 1

        return False, -1


class TokenStar(Token):
    def __init__(self, prev: Token):
        super().__init__(TokenType.STAR)
        self.prev = prev


class TokenPlus(Token):
    def __init__(self, prev: Token):
        super().__init__(TokenType.PLUS)
        self.prev = prev


class TokenOptional(Token):
    def __init__(self, prev: Token):
        super().__init__(TokenType.OPTIONAL)
        self.prev = prev


class TokenGroup(Token):
    def __init__(self, groupOptions: list[list[Token]], groupNum: int):
        super().__init__(TokenType.GROUP)
        self.groupOptions = groupOptions
        self.groupNum = groupNum


class TokenBackreference(Token):
    def __init__(self, groupNum: int):
        super().__init__(TokenType.BACKREFERENCE)
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

        def _compileTokensHelper(pattern: str) -> list[Token]:
            tokens, i = [], 0
            while i < len(pattern):
                c = pattern[i]

                match c:
                    case "*":
                        if len(tokens) == 0: 
                            raise InvalidPattern("No previous pattern to repeat zero or more times")
                        
                        prevToken = tokens.pop()
                        tokens.append(TokenStar(prevToken))

                    case "+":
                        if len(tokens) == 0: 
                            raise InvalidPattern("No previous pattern to repeat one or more times")
                        
                        prevToken = tokens.pop()
                        tokens.append(TokenPlus(prevToken))

                    case "?":
                        if len(tokens) == 0: 
                            raise InvalidPattern("No previous pattern to make optional")
                        
                        prevToken = tokens.pop()
                        tokens.append(TokenOptional(prevToken))

                    case "^":
                        if i != 0: 
                            raise InvalidPattern("'^' must be first character in pattern")

                        tokens.append(TokenStart())

                    case "$":
                        if i != len(pattern) - 1: 
                            raise InvalidPattern("'$' must be last character in pattern")

                        tokens.append(TokenEnd())

                    case "\\":
                        i += 1
                        if i >= len(pattern): 
                            raise InvalidPattern("Expected character class after '\\'")

                        c = pattern[i]
                        if c.isdigit():
                            if int(c) >= self._currGroupNum: 
                                raise InvalidPattern(f"Invalid capture group number '{c}'")
                            
                            tokens.append(TokenBackreference(groupNum=int(c)))
                        else:
                            if c not in "dw\\":
                                raise InvalidPattern(f"Invalid character class '\\{c}'")
                            
                            tokens.append(TokenPredifinedClass(c))

                    case "[":
                        i += 1
                        chars, negated, seenClosingBracket = set(), False, False

                        if pattern[i] == "^":
                            negated = True
                            i += 1

                        while i < len(pattern):
                            if pattern[i] == "]":
                                seenClosingBracket = True
                                break

                            chars.add(pattern[i])
                            i += 1

                        if not seenClosingBracket:
                            raise InvalidPattern("No closing bracket ']'")

                        tokens.append(TokenCharacterClass(chars, negated))

                    case "(":
                        i += 1
                        numOpeningParen, seenClosingParen = 1, False
                        groupOptions, groupNum, subPattern = [], self._currGroupNum, ""
                        self._currGroupNum += 1

                        while i < len(pattern):
                            if pattern[i] == ")" and numOpeningParen == 1:
                                if subPattern != "":
                                    groupOptions.append(_compileTokensHelper(subPattern))
                                
                                seenClosingParen = True
                                break
                            elif pattern[i] == "|" and numOpeningParen == 1:
                                groupOptions.append(_compileTokensHelper(subPattern))
                                subPattern = ""
                            else:
                                if pattern[i] == "(":
                                    numOpeningParen += 1
                                if pattern[i] == ")":
                                    numOpeningParen -= 1
                                subPattern += pattern[i]
                            i += 1
                        
                        if not seenClosingParen:
                            raise InvalidPattern("No closing brace ')'")

                        tokens.append(TokenGroup(groupOptions, groupNum))

                    case _:
                        tokens.append(TokenChar(c))
                i += 1

            return tokens

        return _compileTokensHelper(self.pattern)

    def matchPattern(self, text: str) -> bool:
        textIdx = 0
        while textIdx < len(text):
            foundMatch, _ = self.matchHere(text, textIdx, self.tokens)
            if foundMatch:
                return True
            textIdx += 1
        return False

    def matchHere(self, text: str, textIdx: int, tokens: list[Token]) -> tuple[bool, int]:
        potentialMatchs = [(textIdx, 0)]

        while len(potentialMatchs) != 0:
            currTextIdx, currTokenIdx = potentialMatchs.pop()

            while currTokenIdx < len(tokens):
                currToken = tokens[currTokenIdx]

                match currToken.type:
                    case TokenType.PLUS | TokenType.STAR:
                        if currToken.type == TokenType.STAR:
                            potentialMatchs.append((currTextIdx, currTokenIdx + 1))

                        textEnd = len(text)
                        while currTextIdx != textEnd:
                            matchedPrev, endIdx = self.matchHere(text, currTextIdx, [currToken.prev])
                            if not matchedPrev:
                                break

                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                            currTextIdx = endIdx
                        break
                    
                    case TokenType.GROUP:
                        for subTokens in currToken.groupOptions:
                            foundMatch, endIdx = self.matchHere(text, currTextIdx, subTokens)
                            if not foundMatch:
                                continue
                            captured = self.capturedGroups[currToken.groupNum - 1]
                            captured.start, captured.end = currTextIdx, endIdx

                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                        break

                    case TokenType.OPTIONAL:
                        potentialMatchs.append((currTextIdx, currTokenIdx + 1))
                        matchedPrev, endIdx = self.matchHere(text, currTextIdx, [currToken.prev])
                        if matchedPrev:
                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                        break

                    case TokenType.BACKREFERENCE:
                        captured = self.capturedGroups[currToken.groupNum - 1]
                        capturedText = captured.string(text)

                        endIdx = currTextIdx + len(capturedText)
                        if endIdx <= len(text):    
                            if text[currTextIdx:endIdx] == capturedText:
                                potentialMatchs.append((endIdx, currTokenIdx + 1))
                        break

                    case _:
                        foundMatch, endIdx = currToken.match(text, currTextIdx)
                        if not foundMatch:
                            break
                        
                        currTextIdx = endIdx
                        currTokenIdx += 1

            if currTokenIdx == len(tokens):
                return True, currTextIdx

        return False, -1
