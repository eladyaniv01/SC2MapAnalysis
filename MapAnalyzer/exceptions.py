class OutOfBoundsException(BaseException):
    def __init__(self, p):
        super().__init__()
        self.point = p

    def __str__(self):
        return f"[OutOfBoundsException]Point {self.point} is not inside the grid. No influence added."
