from enum import Enum, auto


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
            c = text[textIdx]
            
            match self.char:
                case "d":
                    if c.isdigit():
                        return True, textIdx + 1
                case "w":
                    if (
                        "a" <= c <= "z"    
                        or "A" <= c <= "Z" 
                        or "0" <= c <= "9"
                        or c == "_"
                    ):
                        return True, textIdx + 1
                case "\\":
                    if c == "\\":
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