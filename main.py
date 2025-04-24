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
                

def matchStdin(re: regex.RE):
    while True:
        try:
            text = input()
        except EOFError:
            return
        
        matches, ok = re.matchPattern(text)
        if not ok:
            print("> No matches")
        else:
            print(colorMatches(matches, text))


def matchFile(re: regex.RE, fileName: str):
    with open(fileName) as f:
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

    try:
        re = regex.RE(args.PATTERN)
    except regex.InvalidPattern as err:
        print(err)
    else:
        if args.file != None:
            matchFile(re, args.file)
        else:
            matchStdin(re)

if __name__ == "__main__":
    main()
