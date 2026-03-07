import unittest
import regex.parser as parser
import regex.nodes as nodes


def run_tests(test: unittest.TestCase, test_cases):
    for case in test_cases:
        exp_ast = case["expected"]["ast"]
        exp_groups = case["expected"]["groups"]

        ast, groups = parser.Parser(case["regex"]).parse()

        test.assertEqual(
            ast,
            exp_ast,
            msg=f"\n{nodes.stringify_node(ast)}\n\n!=\n\n{nodes.stringify_node(exp_ast)}",
        )
        test.assertEqual(groups, exp_groups)


class TestParser(unittest.TestCase):
    def test_parse_literal(self):
        cases = [
            {
                "regex": r"a",
                "expected": {
                    "ast": nodes.Literal("a"),
                    "groups": 0,
                },
            },
            {
                "regex": r"abc",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Literal("a"),
                            nodes.Literal("b"),
                            nodes.Literal("c"),
                        ]
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"",
                "expected": {
                    "ast": nodes.Empty(),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_dot(self):
        cases = [
            {
                "regex": r".",
                "expected": {
                    "ast": nodes.Dot(),
                    "groups": 0,
                },
            },
            {
                "regex": r"a.c",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Literal("a"),
                            nodes.Dot(),
                            nodes.Literal("c"),
                        ]
                    ),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_anchors(self):
        cases = [
            {
                "regex": r"^",
                "expected": {
                    "ast": nodes.StartAnchor(),
                    "groups": 0,
                },
            },
            {
                "regex": r"$",
                "expected": {
                    "ast": nodes.EndAnchor(),
                    "groups": 0,
                },
            },
            {
                "regex": r"^a",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.StartAnchor(),
                            nodes.Literal("a"),
                        ]
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"a$",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Literal("a"),
                            nodes.EndAnchor(),
                        ]
                    ),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_character_class(self):
        cases = [
            {
                "regex": r"[abc]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"a", "b", "c"}, complement=False
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"[^abc]",
                "expected": {
                    "ast": nodes.CharacterClass(chars={"a", "b", "c"}, complement=True),
                    "groups": 0,
                },
            },
            {
                "regex": r"[a-d]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"a", "b", "c", "d"}, complement=False
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"[^a-d]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"a", "b", "c", "d"}, complement=True
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"[a-bd-e]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"a", "b", "d", "e"}, complement=False
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"[^a-bd-e]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"a", "b", "d", "e"}, complement=True
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"[-a]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"a", "-"}, complement=False
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"[b-]",
                "expected": {
                    "ast": nodes.CharacterClass(
                        chars={"b", "-"}, complement=False
                    ),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_meta_sequence(self):
        cases = [
            {
                "regex": r"\d",
                "expected": {
                    "ast": nodes.MetaSequence("d"),
                    "groups": 0,
                },
            },
            {
                "regex": r"\w",
                "expected": {
                    "ast": nodes.MetaSequence("w"),
                    "groups": 0,
                },
            },
            {
                "regex": r"\s",
                "expected": {
                    "ast": nodes.MetaSequence("s"),
                    "groups": 0,
                },
            },
            {
                "regex": r"\b",
                "expected": {
                    "ast": nodes.MetaSequence("b"),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_quantifiers(self):
        cases = [
            {
                "regex": r"a*",
                "expected": {
                    "ast": nodes.Star(nodes.Literal("a")),
                    "groups": 0,
                },
            },
            {
                "regex": r"a+",
                "expected": {
                    "ast": nodes.Plus(nodes.Literal("a")),
                    "groups": 0,
                },
            },
            {
                "regex": r"a?",
                "expected": {
                    "ast": nodes.Optional(nodes.Literal("a")),
                    "groups": 0,
                },
            },
            {
                "regex": r"a{21}",
                "expected": {
                    "ast": nodes.Range(
                        nodes.Literal("a"),
                        min=21,
                        max=21,
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"a{21,69}",
                "expected": {
                    "ast": nodes.Range(
                        node=nodes.Literal("a"),
                        min=21,
                        max=69,
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"a{21,}",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Range(
                                node=nodes.Literal("a"),
                                min=21,
                                max=21,
                            ),
                            nodes.Star(nodes.Literal("a")),
                        ]
                    ),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_lazy_quantifiers(self):
        cases = [
            {
                "regex": r"a*?",
                "expected": {
                    "ast": nodes.Star(nodes.Literal("a"), is_lazy=True),
                    "groups": 0,
                },
            },
            {
                "regex": r"a+?",
                "expected": {
                    "ast": nodes.Plus(nodes.Literal("a"), is_lazy=True),
                    "groups": 0,
                },
            },
            {
                "regex": r"a??",
                "expected": {
                    "ast": nodes.Optional(nodes.Literal("a"), is_lazy=True),
                    "groups": 0,
                },
            },
            {
                "regex": r"a{21}?",
                "expected": {
                    "ast": nodes.Range(
                        nodes.Literal("a"),
                        min=21,
                        max=21,
                        is_lazy=True,
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"a{21,69}?",
                "expected": {
                    "ast": nodes.Range(
                        node=nodes.Literal("a"),
                        min=21,
                        max=69,
                        is_lazy=True,
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"a{21,}?",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Range(
                                node=nodes.Literal("a"),
                                min=21,
                                max=21,
                                is_lazy=True,
                            ),
                            nodes.Star(
                                nodes.Literal("a"),
                                is_lazy=True,
                            ),
                        ]
                    ),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_alteration(self):
        cases = [
            {
                "regex": r"ab|cd|ef",
                "expected": {
                    "ast": nodes.Alternation(
                        [
                            nodes.Sequence(
                                [
                                    nodes.Literal("a"),
                                    nodes.Literal("b"),
                                ]
                            ),
                            nodes.Sequence(
                                [
                                    nodes.Literal("c"),
                                    nodes.Literal("d"),
                                ]
                            ),
                            nodes.Sequence(
                                [
                                    nodes.Literal("e"),
                                    nodes.Literal("f"),
                                ]
                            ),
                        ]
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"ab|",
                "expected": {
                    "ast": nodes.Alternation(
                        [
                            nodes.Sequence(
                                [
                                    nodes.Literal("a"),
                                    nodes.Literal("b"),
                                ]
                            ),
                            nodes.Empty(),
                        ]
                    ),
                    "groups": 0,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_group(self):
        cases = [
            {
                "regex": r"(abc)",
                "expected": {
                    "ast": nodes.Group(
                        1,
                        nodes.Sequence(
                            [
                                nodes.Literal("a"),
                                nodes.Literal("b"),
                                nodes.Literal("c"),
                            ]
                        ),
                    ),
                    "groups": 1,
                },
            },
            {
                "regex": r"(abc|cde)",
                "expected": {
                    "ast": nodes.Group(
                        1,
                        nodes.Alternation(
                            [
                                nodes.Sequence(
                                    [
                                        nodes.Literal("a"),
                                        nodes.Literal("b"),
                                        nodes.Literal("c"),
                                    ]
                                ),
                                nodes.Sequence(
                                    [
                                        nodes.Literal("c"),
                                        nodes.Literal("d"),
                                        nodes.Literal("e"),
                                    ]
                                ),
                            ]
                        ),
                    ),
                    "groups": 1,
                },
            },
            {
                "regex": r"(ab(c))",
                "expected": {
                    "ast": nodes.Group(
                        1,
                        nodes.Sequence(
                            [
                                nodes.Literal("a"),
                                nodes.Literal("b"),
                                nodes.Group(
                                    2,
                                    nodes.Literal("c"),
                                ),
                            ]
                        ),
                    ),
                    "groups": 2,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_perl_ext(self):
        cases = [
            {
                "regex": r"(?:abc)",
                "expected": {
                    "ast": nodes.Group(
                        nodes.Group.NON_CAPTURE_ID,
                        nodes.Sequence(
                            [
                                nodes.Literal("a"),
                                nodes.Literal("b"),
                                nodes.Literal("c"),
                            ]
                        ),
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"(?=abc|cde)",
                "expected": {
                    "ast": nodes.PositiveLookAhead(
                        nodes.Alternation(
                            [
                                nodes.Sequence(
                                    [
                                        nodes.Literal("a"),
                                        nodes.Literal("b"),
                                        nodes.Literal("c"),
                                    ]
                                ),
                                nodes.Sequence(
                                    [
                                        nodes.Literal("c"),
                                        nodes.Literal("d"),
                                        nodes.Literal("e"),
                                    ]
                                ),
                            ]
                        ),
                    ),
                    "groups": 0,
                },
            },
            {
                "regex": r"(?!ab(c))",
                "expected": {
                    "ast": nodes.NegativeLookAhead(
                        nodes.Sequence(
                            [
                                nodes.Literal("a"),
                                nodes.Literal("b"),
                                nodes.Group(
                                    1,
                                    nodes.Literal("c"),
                                ),
                            ]
                        ),
                    ),
                    "groups": 1,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_backreference(self):
        cases = [
            {
                "regex": r"(abc)\1",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Group(
                                1,
                                nodes.Sequence(
                                    [
                                        nodes.Literal("a"),
                                        nodes.Literal("b"),
                                        nodes.Literal("c"),
                                    ]
                                ),
                            ),
                            nodes.BackReference(1),
                        ]
                    ),
                    "groups": 1,
                },
            },
            {
                "regex": r"(ab(c))\1\2",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.Group(
                                1,
                                nodes.Sequence(
                                    [
                                        nodes.Literal("a"),
                                        nodes.Literal("b"),
                                        nodes.Group(
                                            2,
                                            nodes.Literal("c"),
                                        ),
                                    ],
                                ),
                            ),
                            nodes.BackReference(1),
                            nodes.BackReference(2),
                        ]
                    ),
                    "groups": 2,
                },
            },
        ]

        run_tests(self, cases)

    def test_parse_torture_cases(self):
        cases = [
            {
                "regex": r"^((PROD|TEST)-(\d{3,5})-([a-z]{1,2}))$",
                "expected": {
                    "ast": nodes.Sequence(
                        [
                            nodes.StartAnchor(),
                            nodes.Group(
                                1,
                                nodes.Sequence(
                                    [
                                        nodes.Group(
                                            2,
                                            nodes.Alternation(
                                                [
                                                    nodes.Sequence(
                                                        [
                                                            nodes.Literal("P"),
                                                            nodes.Literal("R"),
                                                            nodes.Literal("O"),
                                                            nodes.Literal("D"),
                                                        ]
                                                    ),
                                                    nodes.Sequence(
                                                        [
                                                            nodes.Literal("T"),
                                                            nodes.Literal("E"),
                                                            nodes.Literal("S"),
                                                            nodes.Literal("T"),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ),
                                        nodes.Literal("-"),
                                        nodes.Group(
                                            3,
                                            nodes.Range(
                                                nodes.MetaSequence("d"),
                                                min=3,
                                                max=5,
                                            ),
                                        ),
                                        nodes.Literal("-"),
                                        nodes.Group(
                                            4,
                                            nodes.Range(
                                                nodes.CharacterClass(
                                                    chars={
                                                        chr(i) for i in range(97, 123)
                                                    },
                                                    complement=False,
                                                ),
                                                min=1,
                                                max=2,
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                            nodes.EndAnchor(),
                        ]
                    ),
                    "groups": 4,
                },
            },
        ]

        run_tests(self, cases)
