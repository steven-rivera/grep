import sys
from enum import Enum, auto
from collections import deque
from typing import Optional


class InvalidPattern(Exception):
    pass


class REType(Enum):
    CHAR = auto()  # 'a'
    DOT = auto()  # '.'
    STAR = auto()  # '*'
    PLUS = auto()  # '+'
    OPTIONAL = auto()  # '?'
    START = auto()  # '^'
    END = auto()  # '$'
    CLASS = auto()  # '\d'
    CHAR_CLASS = auto()  # [...]
    GROUP = auto()  # (...|...)
    BACKREFERENCE = auto()  # \1


class RE:
    def __init__(
        self,
        type: REType,
        char: Optional[str] = None,
        chars: Optional[set[str]] = None,
        negated: Optional[bool] = None,
        group: Optional[list[list["RE"]]] = None,
        groupNum: Optional[int] = None,
        prev: Optional["RE"] = None,
    ):
        self.type = type
        self.char = char
        self.chars = chars
        self.negated = negated
        self.group = group
        self.groupNum = groupNum
        self.prev = prev


class Captured:
    def __init__(self, start: Optional[int] = None, end: Optional[int] = None):
        self.start = start
        self.end = end


CapturedGroups = [Captured() for _ in range(10)]


def compileRegex(pattern: str) -> list[RE]:
    currGroupNum = 1
    
    def _compileRegex(pattern: str) -> list[RE]:
        nonlocal currGroupNum
        res = []
        i = 0

        while i < len(pattern):
            c = pattern[i]

            match c:
                case "^":
                    if i != 0:
                        raise InvalidPattern("'^' must be first character in pattern")

                    res.append(RE(type=REType.START, char=c))
                case "$":
                    if i != len(pattern) - 1:
                        raise InvalidPattern("'$' must be last character in pattern")

                    res.append(RE(type=REType.END, char=c))
                case "\\":
                    i += 1
                    if i >= len(pattern):
                        raise InvalidPattern("Expected character class after '\\'")
                    c = pattern[i]

                    if c.isdigit():
                        c = int(c)
                        if c >= currGroupNum:
                            raise InvalidPattern("Invalid capture group number '{c}'")
                        res.append(RE(type=REType.BACKREFERENCE, groupNum=c))

                    else:
                        if c not in "dw\\":
                            raise InvalidPattern(f"Invalid character class '\\{c}'")
                        res.append(RE(type=REType.CLASS, char=c))

                case "[":
                    i += 1
                    negated, seenClosingBracket = False, False
                    charGroup = set()
                    while i < len(pattern):
                        if pattern[i] == "]":
                            seenClosingBracket = True
                            break
                        if pattern[i] == "^":
                            negated = True
                        else:
                            charGroup.add(pattern[i])
                        i += 1

                    if not seenClosingBracket:
                        raise InvalidPattern("No closing bracket ']'")

                    res.append(RE(type=REType.CHAR_CLASS, chars=charGroup, negated=negated))

                case "(":
                    i += 1
                    seenClosingBrace = False
                    patterns, currPattern = [], ""
                    while i < len(pattern):
                        if pattern[i] == ")":
                            if currPattern != "":
                                patterns.append(
                                    _compileRegex(currPattern)
                                )
                            seenClosingBrace = True
                            break
                        elif pattern[i] == "|":
                            patterns.append(
                                _compileRegex(currPattern)
                            )
                            currPattern = ""
                        else:
                            currPattern += pattern[i]
                        i += 1

                    if not seenClosingBrace:
                        raise InvalidPattern("No closing brace ')'")

                    res.append(
                        RE(type=REType.GROUP, group=patterns, groupNum=currGroupNum)
                    )
                    currGroupNum += 1

                case "*":
                    if len(res) == 0:
                        raise InvalidPattern(
                            "No previous pattern to repeat zero or more times"
                        )
                    prev = res.pop()
                    res.append(RE(type=REType.STAR, prev=prev))
                case "+":
                    if len(res) == 0:
                        raise InvalidPattern(
                            "No previous pattern to repeat one or more times"
                        )
                    prev = res.pop()
                    res.append(RE(type=REType.PLUS, prev=prev))
                case "?":
                    if len(res) == 0:
                        raise InvalidPattern("No previous pattern to make optional")
                    prev = res.pop()
                    res.append(RE(type=REType.OPTIONAL, prev=prev))
                case _:
                    res.append(RE(type=REType.CHAR, char=c))

            i += 1

        return res
    
    return _compileRegex(pattern)


def matchPattern(text: str, pattern: list[RE]) -> bool:
    if pattern[0].type == REType.START:
        foundMatch, _ = matchHere(text, 0, pattern, 1)
        return foundMatch

    textIdx = 0
    while True:
        foundMatch, _ = matchHere(text, textIdx, pattern, 0)
        if foundMatch:
            return True

        # Condition checked after to permit zero-length matches
        if textIdx >= len(text):
            break

        textIdx += 1

    return False


def matchHere(
    text: str, textIdx: int, pattern: list[RE], patternIdx: int
) -> tuple[bool, int]:
    textEnd, patternEnd = len(text), len(pattern)

    # Base case: reached end of pattern
    if patternIdx == patternEnd:
        return (True, textIdx)

    # if textIdx == textEnd:
    #     return False

    if pattern[patternIdx].type == REType.PLUS:
        return matchPlus(
            pattern[patternIdx].prev, text, textIdx, pattern, patternIdx + 1
        )

    if pattern[patternIdx].type == REType.OPTIONAL:
        foundMatch, endIdx = matchHere(text, textIdx, pattern, patternIdx + 1)
        if foundMatch:
            return foundMatch, endIdx

        foundPrev, endIdx = matchHere(text, textIdx, [pattern[patternIdx].prev], 0)
        if foundPrev:
            return matchHere(text, endIdx, pattern, patternIdx + 1)

        return False, -1

    if pattern[patternIdx].type == REType.END:
        if textIdx == textEnd:
            return True, textIdx
        return False, -1

    if pattern[patternIdx].type == REType.CLASS and textIdx != textEnd:
        match pattern[patternIdx].char:
            case "d":
                if text[textIdx].isdigit():
                    return matchHere(text, textIdx + 1, pattern, patternIdx + 1)
            case "w":
                if text[textIdx].isalpha():
                    return matchHere(text, textIdx + 1, pattern, patternIdx + 1)
            case "\\":
                if text[textIdx] == "\\":
                    return matchHere(text, textIdx + 1, pattern, patternIdx + 1)

    if pattern[patternIdx].type == REType.CHAR_CLASS and textIdx != textEnd:
        if (
            pattern[patternIdx].negated
            and text[textIdx] not in pattern[patternIdx].chars
        ):
            return matchHere(text, textIdx + 1, pattern, patternIdx + 1)

        if (
            not pattern[patternIdx].negated
            and text[textIdx] in pattern[patternIdx].chars
        ):
            return matchHere(text, textIdx + 1, pattern, patternIdx + 1)

    if pattern[patternIdx].type == REType.GROUP:
        for subPattern in pattern[patternIdx].group:
            foundMatch, endIdx = matchHere(text, textIdx, subPattern, 0)
            if not foundMatch:
                continue

            captured = CapturedGroups[pattern[patternIdx].groupNum - 1]
            captured.start, captured.end = textIdx, endIdx

            foundMatch, endIdx = matchHere(text, endIdx, pattern, patternIdx + 1)
            if foundMatch:
                return foundMatch, endIdx

        return False, -1

    if pattern[patternIdx].type == REType.BACKREFERENCE:
        captured = CapturedGroups[pattern[patternIdx].groupNum - 1]
        subPattern = compileRegex(text[captured.start : captured.end])
        newPattern = subPattern + pattern[patternIdx + 1 :]
        return matchHere(text, textIdx, newPattern, 0)

    if textIdx != textEnd and (
        text[textIdx] == pattern[patternIdx].char or pattern[patternIdx].char == "."
    ):
        return matchHere(text, textIdx + 1, pattern, patternIdx + 1)

    return False, -1


def matchPlus(
    prev: RE, text: str, textIdx: int, pattern: list[RE], patternIdx: str
) -> tuple[bool, int]:

    textEnd = len(text)
    prevTextIdx = textIdx
    matchLengths = []

    while textIdx != textEnd:
        containsPrev, endIdx = matchHere(text, textIdx, [prev], 0)
        if not containsPrev:
            break

        matchLengths.append(endIdx - textIdx)
        textIdx = endIdx

    while textIdx > prevTextIdx:
        foundMatch, endIdx = matchHere(text, textIdx, pattern, patternIdx)
        if foundMatch:
            return True, endIdx
        textIdx -= matchLengths.pop()

    return False, -1


def main():
    if len(sys.argv) < 3:
        print("Expected 2 arguments")

    pattern = sys.argv[2]
    input_line = input()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    pattern = compileRegex(pattern)
    if matchPattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
