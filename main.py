import sys

def matchPattern(text: str, pattern: str) -> bool:
    textIdx = 0

    while True:
        if matchHere(text, textIdx, pattern, 0):
            return True
        
        # Condition checked after to permit zero-length matches
        if textIdx >= len(text):
            break
        
        textIdx += 1

    return False


def matchHere(text: str, textIdx: int, pattern: str, patternIdx: str) -> bool:
    textEnd, patternEnd = len(text), len(pattern)
    
    # Base case: reached end of pattern
    if patternIdx == patternEnd:
        return True
    
    if pattern[patternIdx] == "\\":
        patternIdx += 1
        if patternIdx == patternEnd:
            raise RuntimeError(f"Invalid pattern: Expected character class after '\\'")
        
        if pattern[patternIdx] == "d" and textIdx != textEnd and text[textIdx].isdigit():
            return matchHere(text, textIdx+1, pattern, patternIdx+1)
        if pattern[patternIdx] == "w" and textIdx != textEnd and text[textIdx].isalpha():
            return matchHere(text, textIdx+1, pattern, patternIdx+1)
        

    return False
    


def main():
    if len(sys.argv) < 3:
        print("Expected 2 arguments")
    
    pattern = sys.argv[2]
    input_line = input()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    if matchPattern(input_line, pattern):
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
