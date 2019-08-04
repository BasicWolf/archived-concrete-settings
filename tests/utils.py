import typing


class Match:
    """A rudimentary mock call arguments matcher

    :param match_expr: a callable with single argument returning boolean
    """

    def __init__(self, match_expr: typing.Callable[..., bool]):
        self.match_expr = match_expr

    def __eq__(self, other):
        return self.match_expr(other)
