import argparse
import sys
from pathlib import Path
import regex

BOLD_RED = "\x1b[1;31m"
GREEN = "\x1b[32m"
MAGENTA = "\x1b[35m"
RESET = "\x1b[0m"

ALWAYS = "always"
NEVER = "never"
AUTO = "auto"


def print_matches(
    matches: list[regex.Match],
    file: Path | None,
    line: str,
    line_num: int,
    args: argparse.Namespace,
):

    def fmt(value, color):
        color_output = args.color == ALWAYS or (
            sys.stdout.isatty() and args.color != NEVER
        )
        return f"{color}{value}{RESET}" if color_output else str(value)

    prefix = ""

    if len(args.FILE) > 1 or args.recursive:
        prefix += f"{fmt(file, MAGENTA)}:"
    if args.line_number:
        prefix += f"{fmt(line_num, GREEN)}:"

    if args.only_matching:
        for m in matches:
            print(f"{prefix}{fmt(m.match, BOLD_RED)}")
        return

    s = prefix
    prevEnd = 0

    for m in matches:
        s += f"{line[prevEnd : m.start()]}{fmt(m.match, BOLD_RED)}"
        prevEnd = m.end()

    s += line[prevEnd:]

    print(s)


def search_stdin(pattern: regex.Pattern, args: argparse.Namespace) -> int:
    n = 0
    line_num = 1

    while True:
        try:
            line = input()
        except EOFError:
            return n

        matches = pattern.findall(line)

        if len(matches) == 0:
            continue

        print_matches(
            matches,
            None,
            line,
            line_num,
            args,
        )

        n += len(matches)
        line_num += 1


def search_file(file: Path, pattern: regex.Pattern, args: argparse.Namespace) -> int:
    n = 0

    with open(file) as f:
        try:
            for line_num, line in enumerate(f, start=1):
                line = line.rstrip("\n")
                matches = pattern.findall(line)

                if len(matches) == 0:
                    continue

                print_matches(
                    matches,
                    file,
                    line,
                    line_num,
                    args,
                )

                n += len(matches)
        except UnicodeDecodeError:
            return 0

    return n


def search_dir(dir: Path, pattern: regex.Pattern, args: argparse.Namespace) -> int:
    n = 0
    for dirpath, _, filenames in dir.walk():
        for filename in filenames:
            n += search_file(dirpath / filename, pattern, args)

    return n


def search_files(pattern: regex.Pattern, args: argparse.Namespace) -> int:
    num_matches = 0

    for file in args.FILE:
        path = Path(file)

        if not path.exists():
            print(f"{path}: No such file or directory", file=sys.stderr)
            continue

        if path.is_file():
            num_matches += search_file(path, pattern, args)
        elif args.recursive:
            num_matches += search_dir(path, pattern, args)
        else:
            print(f"{path}: Is a directory", file=sys.stderr)

    return num_matches


def parse_command_line_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "A regular expression pattern matching tool.\n"
            "Search for PATTERN in each FILE. If no FILE is given\n"
            "read from stdin or search files in '.' if -r is specified."
        ),
        formatter_class=argparse.RawTextHelpFormatter,  # Allows newlines in help messages
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help=(
            "if FILE is a directory, recursively search each\n"
            "file in the directory for PATTERN"
        ),
    )
    parser.add_argument(
        "-o",
        "--only-matching",
        action="store_true",
        help="print only the matching text",
    )
    parser.add_argument(
        "-n",
        "--line-number",
        action="store_true",
        help="print line number with output lines",
    )
    parser.add_argument(
        "--color",
        choices=[ALWAYS, NEVER, AUTO],
        default=AUTO,
        help=(
            "always: Always highlight matches in output\n"
            "auto: Highlight matches only when outputing to a TTY\n"
            "never: Never highlight matches in output"
        ),
    )
    parser.add_argument("PATTERN", help="regular expression pattern")
    parser.add_argument("FILE", nargs="*", help="Search for PATTERN in each FILE")

    return parser.parse_args()


def main():
    args = parse_command_line_args()

    try:
        pattern = regex.compile(args.PATTERN)
    except regex.InvalidPattern as e:
        print("Error:", e)
        sys.exit(2)

    num_matches = 0
    if len(args.FILE) > 0:
        num_matches = search_files(pattern, args)
    elif args.recursive:
        num_matches = search_dir(Path("."), pattern, args)
    else:
        num_matches = search_stdin(pattern, args)

    if num_matches == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
