from dataclasses import dataclass, field


@dataclass(frozen=True)
class Match:
    match: str
    span: tuple[int, int]
    captures: dict[int, tuple[int, int]]
    string: str
    _num_groups: int = field(repr=False)  # private field, excluded from repr

    def start(self) -> int:
        return self.span[0]

    def end(self) -> int:
        return self.span[1]

    def group(self, *args: int) -> tuple[str | None, ...] | str | None:
        for group_num in args:
            if group_num < 0 or group_num > self._num_groups:
                raise IndexError("no such group")

        res = []

        for group_num in args:
            span = self.captures.get(group_num, None)

            if span is not None:
                res.append(self.string[span[0] : span[1]])
            elif group_num == 0:
                res.append(self.match)
            else:
                res.append(None)

        if len(res) == 1:
            return res[0]

        return tuple(res)


@dataclass(frozen=True)
class MatchState:
    # Current position in the string
    pos: int
    # Keys are group ID's and values are the start and end index of captured group
    captures: dict[int, tuple[int, int]]

    def __hash__(self):
        return hash((self.pos, tuple(sorted(self.captures.items()))))