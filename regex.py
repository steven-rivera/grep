import tokens

class InvalidPattern(Exception):
    pass


class Match:
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

class RE:
    MAX_CAPTURE_GROUPS = 10

    def __init__(self, pattern: str):
        if pattern == "":
            raise InvalidPattern("Empty pattern in invalid")
        self.pattern = pattern
        self.tokens: list[tokens.Token] = self._compileTokens()
        self.capturedGroups = [None for _ in range(RE.MAX_CAPTURE_GROUPS)]

    def _compileTokens(self):
        self._currGroupNum = 1

        def _compileTokensHelper(pattern: str) -> list[tokens.Token]:
            tkns, idx = [], 0
            while idx < len(pattern):
                char = pattern[idx]

                match char:
                    case "*":
                        if len(tkns) == 0: 
                            raise InvalidPattern("No previous pattern to repeat zero or more times")
                        
                        prevToken = tkns.pop()
                        tkns.append(tokens.TokenStar(prevToken))

                    case "+":
                        if len(tkns) == 0: 
                            raise InvalidPattern("No previous pattern to repeat one or more times")
                        
                        prevToken = tkns.pop()
                        tkns.append(tokens.TokenPlus(prevToken))

                    case "?":
                        if len(tkns) == 0: 
                            raise InvalidPattern("No previous pattern to make optional")
                        
                        prevToken = tkns.pop()
                        tkns.append(tokens.TokenOptional(prevToken))

                    case "^":
                        if idx != 0: 
                            raise InvalidPattern("'^' must be first character in pattern")

                        tkns.append(tokens.TokenStart())

                    case "$":
                        if idx != len(pattern) - 1: 
                            raise InvalidPattern("'$' must be last character in pattern")

                        tkns.append(tokens.TokenEnd())

                    case "\\":
                        idx += 1
                        if idx >= len(pattern): 
                            raise InvalidPattern("Expected character class after '\\'")

                        char = pattern[idx]
                        if char.isdigit():
                            if int(char) >= self._currGroupNum: 
                                raise InvalidPattern(f"Invalid capture group number '{char}'")
                            
                            tkns.append(tokens.TokenBackreference(groupNum=int(char)))
                        else:
                            if char not in "dw\\":
                                raise InvalidPattern(f"Invalid character class '\\{char}'")
                            
                            tkns.append(tokens.TokenPredifinedClass(char))

                    case "[":
                        idx += 1
                        chars, negated, seenClosingBracket = set(), False, False

                        if pattern[idx] == "^":
                            negated = True
                            idx += 1

                        while idx < len(pattern):
                            if pattern[idx] == "]":
                                seenClosingBracket = True
                                break

                            chars.add(pattern[idx])
                            idx += 1

                        if not seenClosingBracket:
                            raise InvalidPattern("No closing bracket ']'")

                        tkns.append(tokens.TokenCharacterClass(chars, negated))

                    case "(":
                        idx += 1
                        numOpeningParen, seenClosingParen = 1, False
                        groupOptions, groupNum, subPattern = [], self._currGroupNum, ""
                        self._currGroupNum += 1

                        while idx < len(pattern):
                            if pattern[idx] == ")" and numOpeningParen == 1:
                                if subPattern != "":
                                    groupOptions.append(_compileTokensHelper(subPattern))
                                
                                seenClosingParen = True
                                break
                            elif pattern[idx] == "|" and numOpeningParen == 1:
                                groupOptions.append(_compileTokensHelper(subPattern))
                                subPattern = ""
                            else:
                                if pattern[idx] == "(":
                                    numOpeningParen += 1
                                if pattern[idx] == ")":
                                    numOpeningParen -= 1
                                subPattern += pattern[idx]
                            idx += 1
                        
                        if not seenClosingParen:
                            raise InvalidPattern("No closing brace ')'")

                        tkns.append(tokens.TokenGroup(groupOptions, groupNum))

                    case "{":
                        if len(tkns) == 0: 
                            raise InvalidPattern("No previous pattern to repeat")
                        
                        idx += 1
                        minimum, maximum = "", ""
                        seenComma, seenClosingBrace = False, False

                        while idx < len(pattern):
                            if pattern[idx].isdigit():
                                if not seenComma:
                                    minimum += pattern[idx]
                                else:
                                    maximum += pattern[idx]
                            elif pattern[idx] == ",":
                                seenComma = True
                            elif pattern[idx] == "}":
                                seenClosingBrace = True
                                break
                            else:
                                raise InvalidPattern(f"Invalid characater '{pattern[idx]}' in range statement")
                            idx += 1

                        if not seenClosingBrace:
                            raise InvalidPattern("No closing brace '}'")
                        if minimum == "":
                            raise InvalidPattern("No minimum value given in range statement")
                        
                        minimum = int(minimum)
                        if maximum != "":
                            maximum = int(maximum)
                        else:
                            maximum = float("inf") if seenComma else minimum

                        prevToken = tkns.pop()
                        tkns.append(tokens.TokenRange(prevToken, int(minimum), maximum))
                        
                    case _:
                        tkns.append(tokens.TokenChar(char))
                idx += 1

            return tkns

        return _compileTokensHelper(self.pattern)

    def matchPattern(self, text: str) -> tuple[list[Match], bool]:
        matches = []
        textIdx = 0
        while textIdx < len(text):
            foundMatch, endIdx = self._matchHere(text, textIdx, self.tokens)
            if foundMatch:
                matches.append(Match(textIdx, endIdx))
                textIdx = endIdx
            else:
                textIdx += 1
        return matches, len(matches) > 0

    def _matchHere(self, text: str, textIdx: int, tkns: list[tokens.Token]) -> tuple[bool, int]:
        potentialMatchs = [(textIdx, 0)]

        while len(potentialMatchs) != 0:
            currTextIdx, currTokenIdx = potentialMatchs.pop()

            while currTokenIdx < len(tkns):
                currToken = tkns[currTokenIdx]

                match currToken.type:
                    case tokens.TokenType.PLUS | tokens.TokenType.STAR:
                        if currToken.type == tokens.TokenType.STAR:
                            potentialMatchs.append((currTextIdx, currTokenIdx + 1))

                        textEnd = len(text)
                        while currTextIdx != textEnd:
                            matchedPrev, endIdx = self._matchHere(text, currTextIdx, [currToken.prev])
                            if not matchedPrev:
                                break

                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                            currTextIdx = endIdx
                        break

                    case tokens.TokenType.RANGE:
                        foundMin = True
                        for _ in range(currToken.min):
                            matchedPrev, endIdx = self._matchHere(text, currTextIdx, [currToken.prev])
                            if not matchedPrev:
                                foundMin = False
                                break
                            currTextIdx = endIdx

                        if not foundMin:
                            break

                        potentialMatchs.append((currTextIdx, currTokenIdx + 1))

                        consumed = currToken.min
                        while consumed < currToken.max:
                            matchedPrev, endIdx = self._matchHere(text, currTextIdx, [currToken.prev])
                            if not matchedPrev:
                                break
                            
                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                            
                            currTextIdx = endIdx
                            consumed += 1

                        break
                    
                    case tokens.TokenType.GROUP:
                        for subTokens in currToken.groupOptions:
                            foundMatch, endIdx = self._matchHere(text, currTextIdx, subTokens)
                            if not foundMatch:
                                continue

                            self.capturedGroups[currToken.groupNum - 1] = text[currTextIdx:endIdx]
                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                        break

                    case tokens.TokenType.OPTIONAL:
                        potentialMatchs.append((currTextIdx, currTokenIdx + 1))
                        matchedPrev, endIdx = self._matchHere(text, currTextIdx, [currToken.prev])
                        if matchedPrev:
                            potentialMatchs.append((endIdx, currTokenIdx + 1))
                        break

                    case tokens.TokenType.BACKREFERENCE:
                        capturedText = self.capturedGroups[currToken.groupNum - 1]

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

            if currTokenIdx == len(tkns):
                return True, currTextIdx

        return False, -1
