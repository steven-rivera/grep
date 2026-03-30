import unittest
import grep
from unittest.mock import patch
from contextlib import ExitStack
from io import StringIO
from grep import GREEN, BOLD_RED, MAGENTA, RESET


def run_tests(test: unittest.TestCase, test_cases):
    for case in test_cases:
        argv = case["argv"]
        stdin = case["stdin"]
        expected = case["expected"]

        stdout = StringIO()

        with ExitStack() as stack:
            stack.enter_context(patch("sys.argv", argv))
            stack.enter_context(patch("sys.stdin", stdin))
            stack.enter_context(patch("sys.stdout", stdout))
            grep.main()

        test.assertEqual(stdout.getvalue(), "".join(expected))


class TestProgramOutput(unittest.TestCase):
    def test_main_when_reading_stdin(self):
        test_cases = [
            {
                "argv": ["grep.py", "--color=never", r"\d"],
                "stdin": StringIO("Line1: 10\nLine2: 42"),
                "expected": [
                    "Line1: 10\n",
                    "Line2: 42\n",
                ],
            },
            {
                "argv": ["grep.py", "--color=never", "-o", r"\d"],
                "stdin": StringIO("Line1: 10\nLine2: 42"),
                "expected": [
                    "1\n",
                    "1\n",
                    "0\n",
                    "2\n",
                    "4\n",
                    "2\n",
                ],
            },
            {
                "argv": ["grep.py", "--color=always", "-o", "-n", r"\d"],
                "stdin": StringIO("Line1: 10\nLine2: 42"),
                "expected": [
                    f"{GREEN}1{RESET}:{BOLD_RED}1{RESET}\n",
                    f"{GREEN}1{RESET}:{BOLD_RED}1{RESET}\n",
                    f"{GREEN}1{RESET}:{BOLD_RED}0{RESET}\n",
                    f"{GREEN}2{RESET}:{BOLD_RED}2{RESET}\n",
                    f"{GREEN}2{RESET}:{BOLD_RED}4{RESET}\n",
                    f"{GREEN}2{RESET}:{BOLD_RED}2{RESET}\n",
                ],
            },
            {
                "argv": ["grep.py", "--color=always", r"(dogs|cats)"],
                "stdin": StringIO("dogs and cats are pets\ndogs are nice"),
                "expected": [
                    f"{BOLD_RED}dogs{RESET} and {BOLD_RED}cats{RESET} are pets\n",
                    f"{BOLD_RED}dogs{RESET} are nice\n",
                ],
            },
        ]

        run_tests(self, test_cases)

    def test_main_when_recursing_directory(self):
        test_cases = [
            {
                "argv": ["grep.py", "--color=never", "-r", r".*ar", "mock/"],
                "stdin": None,
                "expected": [
                    "mock/fruits.txt:pear\n",
                    "mock/subdir/vegetables.txt:carrot\n",
                ],
            },
            {
                "argv": ["grep.py", "--color=always", "-r", r".*ar", "mock/"],
                "stdin": None,
                "expected": [
                    f"{MAGENTA}mock/fruits.txt{RESET}:{BOLD_RED}pear{RESET}\n",
                    f"{MAGENTA}mock/subdir/vegetables.txt{RESET}:{BOLD_RED}car{RESET}rot\n",
                ],
            },
        ]

        run_tests(self, test_cases)
