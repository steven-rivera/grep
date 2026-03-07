import unittest
import regex


def run_tests(test: unittest.TestCase, test_cases):
    for case in test_cases:
        re = case["regex"]
        string = case["string"]
        expected = case["expected"]

        match = regex.compile(re).search(string)

        if match is None:
            test.assertEqual(
                match,
                expected,
                msg=f"Regex '{re}' on '{string}': {expected=} match=None",
            )

            continue

        test.assertIsNotNone(
            expected,
            msg=f"Regex '{re}' on '{string}': expected=None {match=}",
        )

        match = {
            "match": match.match,
            "span": match.span,
            "captures": match.captures, 
        }

        test.assertEqual(
            expected,
            match,
            msg=f"Regex '{re}' on '{string}': {expected=} {match=}",
        )



class TestMatch(unittest.TestCase):
    def test_literals(self):
        cases = [
            {
                "regex": r"a",
                "string": "a",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"a",
                "string": "ba",
                "expected": {"match": "a", "span": (1, 2), "captures": {}},
            },
            {
                "regex": r"dog",
                "string": "dog",
                "expected": {"match": "dog", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"dog",
                "string": "hotdog",
                "expected": {"match": "dog", "span": (3, 6), "captures": {}},
            },
            {
                "regex": r"abc",
                "string": "zzzabczzz",
                "expected": {"match": "abc", "span": (3, 6), "captures": {}},
            },
            {"regex": r"x", "string": "abc", "expected": None},
        ]

        run_tests(self, cases)

    def test_dot(self):
        cases = [
            {
                "regex": r".",
                "string": "xyz",
                "expected": {"match": "x", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r".a",
                "string": "ba",
                "expected": {"match": "ba", "span": (0, 2), "captures": {}},
            },
            {
                "regex": r".b",
                "string": "ab",
                "expected": {"match": "ab", "span": (0, 2), "captures": {}},
            },
            {
                "regex": r"..",
                "string": "abc",
                "expected": {"match": "ab", "span": (0, 2), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_charclass(self):
        cases = [
            {
                "regex": r"[abc]",
                "string": "a",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"[abc]",
                "string": "zzzab",
                "expected": {"match": "a", "span": (3, 4), "captures": {}},
            },
            {
                "regex": r"[xyz]",
                "string": "abcxyz",
                "expected": {"match": "x", "span": (3, 4), "captures": {}},
            },
            {
                "regex": r"[a-f]at",
                "string": "cat",
                "expected": {"match": "cat", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"[a-f]at",
                "string": "hat",
                "expected": None,
            },
            {
                "regex": r"[^a-f]at",
                "string": "cat",
                "expected": None,
            },
            {
                "regex": r"[^a-f]at",
                "string": "hat",
                "expected": {"match": "hat", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"[^a]",
                "string": "ba",
                "expected": {"match": "b", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"[abc]+",
                "string": "zzabcc",
                "expected": {"match": "abcc", "span": (2, 6), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_alternation(self):
        cases = [
            {
                "regex": r"cat|dog",
                "string": "dog",
                "expected": {"match": "dog", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"cat|dog",
                "string": "hotdog",
                "expected": {"match": "dog", "span": (3, 6), "captures": {}},
            },
            {
                "regex": r"dog|cat",
                "string": "cat",
                "expected": {"match": "cat", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"a|b",
                "string": "bbb",
                "expected": {"match": "b", "span": (0, 1), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_star(self):
        cases = [
            {
                "regex": r"a*",
                "string": "aaa",
                "expected": {"match": "aaa", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"a*",
                "string": "baaa",
                "expected": {"match": "", "span": (0, 0), "captures": {}},
            },
            {
                "regex": r"ba*",
                "string": "baaa",
                "expected": {"match": "baaa", "span": (0, 4), "captures": {}},
            },
            {
                "regex": r"ab*c",
                "string": "ac",
                "expected": {"match": "ac", "span": (0, 2), "captures": {}},
            },
            {
                "regex": r"ab*c",
                "string": "abbbc",
                "expected": {"match": "abbbc", "span": (0, 5), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_plus(self):
        cases = [
            {
                "regex": r"a+",
                "string": "aaa",
                "expected": {"match": "aaa", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"a+",
                "string": "baaa",
                "expected": {"match": "aaa", "span": (1, 4), "captures": {}},
            },
            {
                "regex": r"ab+c",
                "string": "abbc",
                "expected": {"match": "abbc", "span": (0, 4), "captures": {}},
            },
            {"regex": r"ab+c", "string": "ac", "expected": None},
        ]

        run_tests(self, cases)

    def test_optional(self):
        cases = [
            {
                "regex": r"a?",
                "string": "a",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"ab?",
                "string": "abbb",
                "expected": {"match": "ab", "span": (0, 2), "captures": {}},
            },
            {
                "regex": r"ab?",
                "string": "aaaa",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"colou?r",
                "string": "color",
                "expected": {"match": "color", "span": (0, 5), "captures": {}},
            },
            {
                "regex": r"colou?r",
                "string": "colour",
                "expected": {"match": "colour", "span": (0, 6), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_range(self):
        cases = [
            {
                "regex": r"a{2}",
                "string": "aaa",
                "expected": {"match": "aa", "span": (0, 2), "captures": {}},
            },
            {
                "regex": r"a{2,4}",
                "string": "aaaaa",
                "expected": {"match": "aaaa", "span": (0, 4), "captures": {}},
            },
            {
                "regex": r"a{1,3}",
                "string": "aaaa",
                "expected": {"match": "aaa", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"ca{3,}t",
                "string": "caaaat",
                "expected": {"match": "caaaat", "span": (0, 6), "captures": {}},
            },
            {
                "regex": r"ca{3,}t",
                "string": "caat",
                "expected": None,
            },
            {
                "regex": r"(\d{3}-){2}\d{4}",
                "string": "123-456-7890",
                "expected": {
                    "match": "123-456-7890",
                    "span": (0, 12),
                    "captures": {1: (4, 8)},
                },
            },
            {"regex": r"(\d{3}-){2}\d{4}", "string": "123-45-7890", "expected": None},
        ]

        run_tests(self, cases)

    def test_lazy_repetition(self):
        cases = [
            {
                "regex": r"a*?",
                "string": "aaa",
                "expected": {"match": "", "span": (0, 0), "captures": {}},
            },
            {
                "regex": r"ba*?",
                "string": "b",
                "expected": {"match": "b", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"a+?",
                "string": "aaa",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"ba+?",
                "string": "baaa",
                "expected": {"match": "ba", "span": (0, 2), "captures": {}},
            },
            {
                "regex": r"(a|aa)+?",
                "string": "aaa",
                "expected": {"match": "a", "span": (0, 1), "captures": {1: (0, 1)}},
            },
            {
                "regex": r"a??",
                "string": "a",
                "expected": {"match": "", "span": (0, 0), "captures": {}},
            },
            {
                "regex": r"a{3}?",
                "string": "aaaaaa",
                "expected": {"match": "aaa", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"a{3,}?",
                "string": "aaaaaa",
                "expected": {"match": "aaa", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"a{2,5}?",
                "string": "aaaaaa",
                "expected": {"match": "aa", "span": (0, 2), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_groups(self):
        cases = [
            {
                "regex": r"(abc)",
                "string": "abc",
                "expected": {"match": "abc", "span": (0, 3), "captures": {1: (0, 3)}},
            },
            {
                "regex": r"(ab)c",
                "string": "abc",
                "expected": {"match": "abc", "span": (0, 3), "captures": {1: (0, 2)}},
            },
            {
                "regex": r"a(bc)",
                "string": "abc",
                "expected": {"match": "abc", "span": (0, 3), "captures": {1: (1, 3)}},
            },
            {
                "regex": r"(ab)*",
                "string": "abab",
                "expected": {"match": "abab", "span": (0, 4), "captures": {1: (2, 4)}},
            },
        ]

        run_tests(self, cases)

    def test_nested_groups(self):
        cases = [
            {
                "regex": r"(a(bc))",
                "string": "abc",
                "expected": {
                    "match": "abc",
                    "span": (0, 3),
                    "captures": {1: (0, 3), 2: (1, 3)},
                },
            },
            {
                "regex": r"((ab)c)",
                "string": "abc",
                "expected": {
                    "match": "abc",
                    "span": (0, 3),
                    "captures": {1: (0, 3), 2: (0, 2)},
                },
            },
        ]

        run_tests(self, cases)

    def test_backrefs(self):
        cases = [
            {
                "regex": r"(a)\1",
                "string": "aa",
                "expected": {"match": "aa", "span": (0, 2), "captures": {1: (0, 1)}},
            },
            {
                "regex": r"(ab)\1",
                "string": "abab",
                "expected": {"match": "abab", "span": (0, 4), "captures": {1: (0, 2)}},
            },
            {
                "regex": r"(pop) goes \1{3}",
                "string": "pop goes poppoppop",
                "expected": {
                    "match": "pop goes poppoppop",
                    "span": (0, 18),
                    "captures": {1: (0, 3)},
                },
            },
            {
                "regex": r"(pop) goes \1{3}",
                "string": "pop goes poppop",
                "expected": None,
            },
        ]

        run_tests(self, cases)

    def test_multiple_backrefs(self):
        cases = [
            {
                "regex": r"(\d+) (\w+) squares and \1 \2 circles",
                "string": "3 red squares and 3 red circles",
                "expected": {
                    "match": "3 red squares and 3 red circles",
                    "span": (0, 31),
                    "captures": {1: (0, 1), 2: (2, 5)},
                },
            },
            {
                "regex": r"(c.t|d.g) and (f..h|b..d), \1 with \2",
                "string": "cat and fish, cat with fish",
                "expected": {
                    "match": "cat and fish, cat with fish",
                    "span": (0, 27),
                    "captures": {1: (0, 3), 2: (8, 12)},
                },
            },
            {
                "regex": r"(c.t|d.g) and (f..h|b..d), \1 with \2",
                "string": "bat and fish, cat with fish",
                "expected": None,
            },
        ]

        run_tests(self, cases)

    def test_nested_backrefs(self):
        cases = [
            {
                "regex": r"('(cat) and \2') is the same as \1",
                "string": "'cat and cat' is the same as 'cat and cat'",
                "expected": {
                    "match": "'cat and cat' is the same as 'cat and cat'",
                    "span": (0, 42),
                    "captures": {1: (0, 13), 2: (1, 4)},
                },
            },
            {
                "regex": r"('(cat) and \2') is the same as \1",
                "string": "'cat and cat' is the same as 'cat and dog'",
                "expected": None,
            },
            {
                "regex": r"((c.t|d.g) and (f..h|b..d)), \2 with \3, \1",
                "string": "cat and fish, cat with fish, cat and fish",
                "expected": {
                    "match": "cat and fish, cat with fish, cat and fish",
                    "span": (0, 41),
                    "captures": {1: (0, 12), 2: (0, 3), 3: (8, 12)},
                },
            },
            {
                "regex": r"((c.t|d.g) and (f..h|b..d)), \2 with \3, \1",
                "string": "bat and fish, bat with fish, bat and fish",
                "expected": None,
            },
        ]

        run_tests(self, cases)

    def test_start_anchor(self):
        cases = [
            {
                "regex": r"^a",
                "string": "abc",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {"regex": r"^a", "string": "ba", "expected": None},
        ]

        run_tests(self, cases)

    def test_end_anchor(self):
        cases = [
            {
                "regex": r"a$",
                "string": "ba",
                "expected": {"match": "a", "span": (1, 2), "captures": {}},
            },
            {"regex": r"a$", "string": "ab", "expected": None},
        ]

        run_tests(self, cases)

    def test_start_and_end_anchor(self):
        cases = [
            {
                "regex": r"^abc$",
                "string": "abc",
                "expected": {"match": "abc", "span": (0, 3), "captures": {}},
            },
            {"regex": r"^abc$", "string": "zabc", "expected": None},
        ]

        run_tests(self, cases)

    def test_metasequences(self):
        cases = [
            {
                "regex": r"\d+",
                "string": "abc123",
                "expected": {"match": "123", "span": (3, 6), "captures": {}},
            },
            {
                "regex": r"\D+",
                "string": "abc123",
                "expected": {"match": "abc", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"\w+",
                "string": "!!!abc123",
                "expected": {"match": "abc123", "span": (3, 9), "captures": {}},
            },
            {
                "regex": r"\W+",
                "string": "!!!abc123",
                "expected": {"match": "!!!", "span": (0, 3), "captures": {}},
            },
            {
                "regex": r"\s+",
                "string": "a   b",
                "expected": {"match": "   ", "span": (1, 4), "captures": {}},
            },
            {
                "regex": r"\S+",
                "string": "   ab   ",
                "expected": {"match": "ab", "span": (3, 5), "captures": {}},
            },
            {
                "regex": r"a\b",
                "string": "aaa bbb",
                "expected": {"match": "a", "span": (2, 3), "captures": {}},
            },
            {
                "regex": r"a\b",
                "string": "aaa",
                "expected": {"match": "a", "span": (2, 3), "captures": {}},
            },
            {
                "regex": r"\ba",
                "string": "aaa",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"a\b",
                "string": "aaabbb",
                "expected": None,
            },
            {
                "regex": r"\ba",
                "string": "baa",
                "expected": None,
            },
            {
                "regex": r"#\b",
                "string": "#1",
                "expected": {"match": "#", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"#\b",
                "string": "# 1",
                "expected": None,
            },
            {
                "regex": r"#\b",
                "string": "#",
                "expected": None,
            },
            {
                "regex": r"\b#",
                "string": "#",
                "expected": None,
            },
            {
                "regex": r"\b#",
                "string": "a#",
                "expected": {"match": "#", "span": (1, 2), "captures": {}},
            },
            {
                "regex": r"\ba\b",
                "string": "a",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"\ba\b",
                "string": "c a t",
                "expected": {"match": "a", "span": (2, 3), "captures": {}},
            },
            {
                "regex": r"\ba\b",
                "string": "at",
                "expected": None,
            },
            {
                "regex": r"\ba\b",
                "string": "cat",
                "expected": None,
            },
            {
                "regex": r"\ba\b",
                "string": "ca",
                "expected": None,
            },
            {
                "regex": r"a\B",
                "string": "a",
                "expected": None,
            },
            {
                "regex": r"a\B",
                "string": "ab",
                "expected": {"match": "a", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"a\B",
                "string": "a#",
                "expected": None,
            },
            {
                "regex": r"#\B",
                "string": "#",
                "expected": {"match": "#", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"#\B",
                "string": "#!",
                "expected": {"match": "#", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"#\B",
                "string": "#1",
                "expected": None,
            },
            {
                "regex": r"\Ba",
                "string": "a",
                "expected": None,
            },
            {
                "regex": r"\B#",
                "string": "#",
                "expected": {"match": "#", "span": (0, 1), "captures": {}},
            },
            {
                "regex": r"\B#",
                "string": "a#",
                "expected": None,
            },
            {
                "regex": r"\B#",
                "string": "!#",
                "expected": {"match": "#", "span": (1, 2), "captures": {}},
            },
            {
                "regex": r"\Ba\B",
                "string": "a",
                "expected": None,
            },
            {
                "regex": r"\Ba\B",
                "string": "cat",
                "expected": {"match": "a", "span": (1, 2), "captures": {}},
            },
        ]

        run_tests(self, cases)

    def test_complex_patterns(self):
        cases = [
            {
                "regex": r"(ab)+",
                "string": "ababab",
                "expected": {
                    "match": "ababab",
                    "span": (0, 6),
                    "captures": {1: (4, 6)},
                },
            },
            {
                "regex": r"(ab)*c",
                "string": "ababababc",
                "expected": {
                    "match": "ababababc",
                    "span": (0, 9),
                    "captures": {1: (6, 8)},
                },
            },
            {
                "regex": r"(a|b)+",
                "string": "abba",
                "expected": {"match": "abba", "span": (0, 4), "captures": {1: (3, 4)}},
            },
            {
                "regex": r"(ab|cd)+",
                "string": "abcdab",
                "expected": {
                    "match": "abcdab",
                    "span": (0, 6),
                    "captures": {1: (4, 6)},
                },
            },
            {
                "regex": r"^(a|b)+(cd)*e$",
                "string": "ababcdcdcde",
                "expected": {
                    "match": "ababcdcdcde",
                    "span": (0, 11),
                    "captures": {1: (3, 4), 2: (8, 10)},
                },
            },
            {
                "regex": r"(\w+) \1",
                "string": "hello hello world",
                "expected": {
                    "match": "hello hello",
                    "span": (0, 11),
                    "captures": {1: (0, 5)},
                },
            },
        ]

        run_tests(self, cases)

    def test_torture_cases(self):
        cases = [
            {
                "regex": r"(a*)*",
                "string": "aaa",
                "expected": {
                    "match": "aaa",
                    "span": (0, 3),
                    "captures": {1: (3, 3)},
                },
            },
            {
                "regex": r"(ab*)*",
                "string": "abbbab",
                "expected": {
                    "match": "abbbab",
                    "span": (0, 6),
                    "captures": {1: (4, 6)},
                },
            },
            {
                "regex": r"(a|ab)*",
                "string": "abaab",
                "expected": {
                    "match": "abaab",
                    "span": (0, 5),
                    "captures": {1: (3, 5)},
                },
            },
            {
                "regex": r"(a(b(c)))",
                "string": "abc",
                "expected": {
                    "match": "abc",
                    "span": (0, 3),
                    "captures": {1: (0, 3), 2: (1, 3), 3: (2, 3)},
                },
            },
        ]

        run_tests(self, cases)


if __name__ == "__main__":
    unittest.main(failfast=True)
