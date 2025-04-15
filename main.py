import sys
import regex


def main():
    if len(sys.argv) < 3:
        print("Expected 2 arguments")

    pattern = sys.argv[2]
    input_line = input()

    if sys.argv[1] != "-E":
        print("Expected first argument to be '-E'")
        exit(1)

    r = regex.RE(pattern)
    if r.matchPattern(input_line):
        exit(0)
    else:
        exit(1)



if __name__ == "__main__":
    main()
