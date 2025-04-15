import argparse, regex


def colorMatches(matches: list[regex.Match], text: str) -> str:
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    
    colorStr = ""

    prevEnd = 0
    for m in matches: 
        colorStr += text[prevEnd:m.start]
        colorStr += f"{BOLD_RED}{text[m.start:m.end]}{RESET}"
        prevEnd = m.end

    colorStr += text[prevEnd:]

    return colorStr
                

def readStdin(args: argparse.Namespace):
    re = regex.RE(args.PATTERN)
    
    while True:
        try:
            text = input()
        except EOFError:
            break
        else:
            matches, ok = re.matchPattern(text)
            if not ok:
                print("> No matches")
            else:
                print(colorMatches(matches, text))


def readFile(args: argparse.Namespace):
    re = regex.RE(args.PATTERN)

    with open(args.file) as f:
        for lineNum, line in enumerate(f, start=1):
            line = line.strip()
            matches, ok = re.matchPattern(line)
            if ok:
                print(f"{lineNum}: {colorMatches(matches, line)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("PATTERN", help="regular expression pattern")
    parser.add_argument("-f", "--file", help="file to search for all occurences of pattern. If no file is provided read from stdin")

    args = parser.parse_args()
    
    if args.file != None:
        readFile(args)
    else:
        readStdin(args)

if __name__ == "__main__":
    main()
