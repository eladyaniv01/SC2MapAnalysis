from typing import Tuple


class OutOfBoundsException(BaseException):
    def __init__(self, p: Tuple[int, int]) -> None:
        super().__init__()
        self.point = p

    def __str__(self) -> str:
        return f"[OutOfBoundsException]Point {self.point} is not inside the grid. No influence added."
