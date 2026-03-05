import regex
import argparse


def highlight_matches(matches: list[regex.Match], text: str) -> str:
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    s = ""

    prevEnd = 0
    for m in matches:
        s += f"{text[prevEnd : m.start()]}{BOLD_RED}{text[m.start() : m.end()]}{RESET}"
        prevEnd = m.end()

    s += text[prevEnd:]

    return s


def search_stdin(pattern: regex.Pattern):
    while True:
        try:
            text = input()
        except EOFError:
            return

        matches = pattern.findall(text)

        if len(matches) == 0:
            print("> No matches")
            continue

        print(highlight_matches(matches, text))


def search_file(pattern: regex.Pattern, file: str):
    try: 
        with open(file) as f:
            for line_num, line in enumerate(f, start=1):
                line = line.rstrip("\n")
                matches = pattern.findall(line)

                if len(matches) == 0:
                    continue

                print(f"{line_num}: {highlight_matches(matches, line)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("PATTERN", help="regular expression pattern")
    parser.add_argument(
        "-f",
        "--file",
        help="file to search for all occurences of pattern. If no file is provided read from stdin",
    )

    args = parser.parse_args()

    try:
        pattern = regex.compile(args.PATTERN)
    except regex.InvalidPattern as e:
        print(f"Error: {e}")
    else:
        if args.file is not None:
            search_file(pattern, args.file)
        else:
            search_stdin(pattern)


if __name__ == "__main__":
    main()
