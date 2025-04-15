import unittest, regex


class TestMatchPattern(unittest.TestCase):
    def run_match_test(self, test_cases):
        for index, case in enumerate(test_cases):
            with self.subTest(f"Case: {index}"):
                result = regex.RE(case["pattern"]).matchPattern(case["text"])
                self.assertEqual(
                    result,
                    case["expected"],
                    msg=f"Text: {case["text"]}, Pattern: {case["pattern"]}",
                )

    def test_match_literal_character(self):
        test_cases = [
            {"text": "dog", "pattern": r"o", "expected": True},
            {"text": "dog", "pattern": r"f", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_digits(self):
        test_cases = [
            {"text": "123", "pattern": r"\d", "expected": True},
            {"text": "apple", "pattern": r"\d", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_alphanumeric_characters(self):
        test_cases = [
            {"text": "word", "pattern": r"\w", "expected": True},
            {"text": "$!?", "pattern": r"\w", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_positive_character_groups(self):
        test_cases = [
            {"text": "a", "pattern": r"[abcd]", "expected": True},
            {"text": "efgh", "pattern": r"[abcd]", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_negative_character_groups(self):
        test_cases = [
            {"text": "apple", "pattern": r"[^xyz]", "expected": True},
            {"text": "banana", "pattern": r"[^anb]", "expected": False},
            {"text": "orange", "pattern": r"[^opq]", "expected": True},
        ]

        self.run_match_test(test_cases)

    def test_match_combining_character_classes(self):
        test_cases = [
            {"text": "sally has 3 apples", "pattern": r"\d apple", "expected": True},
            {"text": "sally has 1 orange", "pattern": r"\d apple", "expected": False},
            {
                "text": "sally has 124 apples",
                "pattern": r"\d\d\d apples",
                "expected": True,
            },
            {"text": "sally has 5 apples", "pattern": r"\\d apples", "expected": False},
            {"text": "sally has 3 dogs", "pattern": r"\d \w\w\ws", "expected": True},
            {"text": "sally has 4 dogs", "pattern": r"\d \w\w\ws", "expected": True},
            {"text": "sally has 1 dog", "pattern": r"\d \w\w\ws", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_start_of_string(self):
        test_cases = [
            {"text": "log", "pattern": r"^log", "expected": True},
            {"text": "slog", "pattern": r"^log", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_end_of_string(self):
        test_cases = [
            {"text": "cat", "pattern": r"cat$", "expected": True},
            {"text": "cats", "pattern": r"cat$", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_one_or_more_times(self):
        test_cases = [
            {"text": "cat", "pattern": r"ca+t", "expected": True},
            {"text": "caaats", "pattern": r"ca+at", "expected": True},
            {"text": "act", "pattern": r"ca+t", "expected": False},
            {"text": "ca", "pattern": r"ca+t", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_zero_or_more_times(self):
        test_cases = [
            {"text": "cat", "pattern": r"ca?t", "expected": True},
            {"text": "act", "pattern": r"ca?t", "expected": True},
            {"text": "dog", "pattern": r"ca?t", "expected": False},
            {"text": "cag", "pattern": r"ca?t", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_wildcard(self):
        test_cases = [
            {"text": "cat", "pattern": r"c.t", "expected": True},
            {"text": "car", "pattern": r"c.t", "expected": False},
            {"text": "goøö0Ogol", "pattern": r"g.+gol", "expected": True},
            {"text": "gol", "pattern": r"g.+gol", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_alternation(self):
        test_cases = [
            {"text": "a cat", "pattern": r"a (cat|dog)", "expected": True},
            {
                "text": "a dog and cats",
                "pattern": r"a (cat|dog) and (cat|dog)s",
                "expected": True,
            },
            {"text": "a cow", "pattern": r"a (cat|dog)", "expected": False},
        ]

        self.run_match_test(test_cases)

    def test_match_single_backreference(self):
        test_cases = [
            {"text": "cat and cat", "pattern": r"(cat) and \1", "expected": True},
            {"text": "cat and dog", "pattern": r"(cat) and \1", "expected": False},
            {
                "text": "grep 101 is doing grep 101 times",
                "pattern": r"(\w\w\w\w \d\d\d) is doing \1 times",
                "expected": True,
            },
            {
                "text": "$?! 101 is doing $?! 101 times",
                "pattern": r"(\w\w\w \d\d\d) is doing \1 times",
                "expected": False,
            },
            {
                "text": "grep yes is doing grep yes times",
                "pattern": r"(\w\w\w\w \d\d\d) is doing \1 times",
                "expected": False,
            },
            {
                "text": "abcd is abcd, not efg",
                "pattern": r"([abcd]+) is \1, not [^xyz]+",
                "expected": True,
            },
            {
                "text": "efgh is efgh, not efg",
                "pattern": r"([abcd]+) is \1, not [^xyz]+",
                "expected": False,
            },
            {
                "text": "abcd is abcd, not xyz",
                "pattern": r"([abcd]+) is \1, not [^xyz]+",
                "expected": False,
            },
            {
                "text": "this starts and ends with this",
                "pattern": r"^(\w+) starts and ends with \1$",
                "expected": True,
            },
            {
                "text": "that starts and ends with this",
                "pattern": r"^(this) starts and ends with \1$",
                "expected": False,
            },
            {
                "text": "this starts and ends with this?",
                "pattern": r"^(this) starts and ends with \1$",
                "expected": False,
            },
            {
                "text": "once a dreaaamer, always a dreaaamer",
                "pattern": r"once a (drea+mer), alwaysz? a \1",
                "expected": True,
            },
            {
                "text": "once a dreaaamer, always a dreamer",
                "pattern": r"once a (drea+mer), alwaysz? a \1",
                "expected": False,
            },
            {
                "text": "once a dremer, always a dreaaamer",
                "pattern": r"once a (drea+mer), alwaysz? a \1",
                "expected": False,
            },
            {
                "text": "once a dreaaamer, alwayszzz a dreaaamer",
                "pattern": r"once a (drea+mer), alwaysz? a \1",
                "expected": False,
            },
            {
                "text": "bugs here and bugs there",
                "pattern": r"(b..s|c..e) here and \1 there",
                "expected": True,
            },
            {
                "text": "bugz here and bugs there",
                "pattern": r"(b..s|c..e) here and \1 there",
                "expected": False,
            },
        ]

        self.run_match_test(test_cases)

    def test_match_multiple_backreference(self):
        test_cases = [
            {
                "text": "3 red squares and 3 red circles",
                "pattern": r"(\d+) (\w+) squares and \1 \2 circles",
                "expected": True,
            },
            {
                "text": "3 red squares and 4 red circles",
                "pattern": r"(\d+) (\w+) squares and \1 \2 circles",
                "expected": False,
            },
            {
                "text": "grep 101 is doing grep 101 times",
                "pattern": r"(\w\w\w\w) (\d\d\d) is doing \1 \2 times",
                "expected": True,
            },
            {
                "text": "$?! 101 is doing $?! 101 times",
                "pattern": r"(\w\w\w) (\d\d\d) is doing \1 \2 times",
                "expected": False,
            },
            {
                "text": "grep yes is doing grep yes times",
                "pattern": r"(\w\w\w\w) (\d\d\d) is doing \1 \2 times",
                "expected": False,
            },
            {
                "text": "abc-def is abc-def, not efg",
                "pattern": r"([abc]+)-([def]+) is \1-\2, not [^xyz]+",
                "expected": True,
            },
            {
                "text": "efg-hij is efg-hij, not efg",
                "pattern": r"([abc]+)-([def]+) is \1-\2, not [^xyz]+",
                "expected": False,
            },
            {
                "text": "abc-def is abc-def, not xyz",
                "pattern": r"([abc]+)-([def]+) is \1-\2, not [^xyz]+",
                "expected": False,
            },
            {
                "text": "apple pie, apple and pie",
                "pattern": r"^(\w+) (\w+), \1 and \2$",
                "expected": True,
            },
            {
                "text": "pineapple pie, pineapple and pie",
                "pattern": r"^(apple) (\w+), \1 and \2$",
                "expected": False,
            },
            {
                "text": "apple pie, apple and pies",
                "pattern": r"^(\w+) (pie), \1 and \2$",
                "expected": False,
            },
            {
                "text": "howwdy hey there, howwdy hey",
                "pattern": r"(how+dy) (he?y) there, \1 \2",
                "expected": True,
            },
            {
                "text": "hody hey there, howwdy hey",
                "pattern": r"(how+dy) (he?y) there, \1 \2",
                "expected": False,
            },
            {
                "text": "howwdy heeey there, howwdy heeey",
                "pattern": r"(how+dy) (he?y) there, \1 \2",
                "expected": False,
            },
            {
                "text": "cat and fish, cat with fish",
                "pattern": r"(c.t|d.g) and (f..h|b..d), \1 with \2",
                "expected": True,
            },
            {
                "text": "bat and fish, cat with fish",
                "pattern": r"(c.t|d.g) and (f..h|b..d), \1 with \2",
                "expected": False,
            },
        ]

        self.run_match_test(test_cases)

    def test_match_nested_backreference(self):
        test_cases = [
            {
                "text": "'cat and cat' is the same as 'cat and cat'",
                "pattern": r"('(cat) and \2') is the same as \1",
                "expected": True,
            },
            {
                "text": "'cat and cat' is the same as 'cat and dog'",
                "pattern": r"('(cat) and \2') is the same as \1",
                "expected": False,
            },
            {
                "text": "grep 101 is doing grep 101 times, and again grep 101 times",
                "pattern": r"((\w\w\w\w) (\d\d\d)) is doing \2 \3 times, and again \1 times",
                "expected": True,
            },
            {
                "text": "$?! 101 is doing $?! 101 times, and again $?! 101 times",
                "pattern": r"((\w\w\w) (\d\d\d)) is doing \2 \3 times, and again \1 times",
                "expected": False,
            },
            {
                "text": "grep yes is doing grep yes times, and again grep yes times",
                "pattern": r"((\w\w\w\w) (\d\d\d)) is doing \2 \3 times, and again \1 times",
                "expected": False,
            },
            {
                "text": "abc-def is abc-def, not efg, abc, or def",
                "pattern": r"(([abc]+)-([def]+)) is \1, not ([^xyz]+), \2, or \3",
                "expected": True,
            },
            {
                "text": "efg-hij is efg-hij, not klm, efg, or hij",
                "pattern": r"(([abc]+)-([def]+)) is \1, not ([^xyz]+), \2, or \3",
                "expected": False,
            },
            {
                "text": "abc-def is abc-def, not xyz, abc, or def",
                "pattern": r"(([abc]+)-([def]+)) is \1, not ([^xyz]+), \2, or \3",
                "expected": False,
            },
            {
                "text": "apple pie is made of apple and pie. love apple pie",
                "pattern": r"^((\w+) (\w+)) is made of \2 and \3. love \1$",
                "expected": True,
            },
            {
                "text": "pineapple pie is made of apple and pie. love apple pie",
                "pattern": r"^((apple) (\w+)) is made of \2 and \3. love \1$",
                "expected": False,
            },
            {
                "text": "apple pie is made of apple and pie. love apple pies",
                "pattern": r"^((\w+) (pie)) is made of \2 and \3. love \1$",
                "expected": False,
            },
            {
                "text": "'howwdy hey there' is made up of 'howwdy' and 'hey'. howwdy hey there",
                "pattern": r"'((how+dy) (he?y) there)' is made up of '\2' and '\3'. \1",
                "expected": True,
            },
            {
                "text": "'hody hey there' is made up of 'hody' and 'hey'. hody hey there",
                "pattern": r"'((how+dy) (he?y) there)' is made up of '\2' and '\3'. \1",
                "expected": False,
            },
            {
                "text": "howwdy heeey there' is made up of 'howwdy' and 'heeey'. howwdy heeey there",
                "pattern": r"'((how+dy) (he?y) there)' is made up of '\2' and '\3'. \1",
                "expected": False,
            },
            {
                "text": "cat and fish, cat with fish, cat and fish",
                "pattern": r"((c.t|d.g) and (f..h|b..d)), \2 with \3, \1",
                "expected": True,
            },
            {
                "text": "bat and fish, bat with fish, bat and fish",
                "pattern": r"((c.t|d.g) and (f..h|b..d)), \2 with \3, \1",
                "expected": False,
            },
        ]

        self.run_match_test(test_cases)