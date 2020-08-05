from typing import Tuple


class CustomDeprecationWarning(BaseException):
    def __init__(self, oldarg=None, newarg=None):
        self.old = oldarg
        self.new = newarg

    def __str__(self) -> str:
        return f"[DeprecationWarning] Passing `{self.old}` argument is deprecated, and will have no effect,\nUse `{self.new}` instead"


class OutOfBoundsException(BaseException):
    def __init__(self, p: Tuple[int, int]) -> None:
        super().__init__()
        self.point = p

    def __str__(self) -> str:
        return f"[OutOfBoundsException]Point {self.point} is not inside the grid. No influence added."
