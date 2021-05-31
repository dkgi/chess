from __future__ import annotations
import logging
import abc
from enum import Enum

LOG: logging.Logger = logging.getLogger(__file__)


class Color(Enum):
    BLACK = 0
    WHITE = 1


class Figure:
    def __init__(self, color: Color) -> None:
        self._color: Color = color

    def __str__(self) -> str:
        color = "\033[30m" if self._color == Color.BLACK else "\033[37m"
        return f"{color}{self.name()}"

    @abc.abstractmethod
    def name(self) -> str:
        pass


class Pawn(Figure):
    def name(self) -> str:
        return "P"


class Board:
    def __init__(self) -> None:
        # self.fields[1][a] is bottom left, self.fields[1][h] is bottom right
        self.fields: list[list[Figure | None]] =  [[None] * 8] * 8

        self.fields[1] = [Pawn(Color.WHITE)] * 8
        self.fields[6] = [Pawn(Color.BLACK)] * 8

    def __str__(self) -> str:
        color = "\033[102m"
        clear = "\033[0m"
        lines = [
            "".join([
                f"{color}{field or ' '}{clear}"
                for field
                in row
            ])
            for row in
            self.fields
        ]
        return "\n".join(reversed(lines))


def main() -> None:
    board = Board()
    LOG.info(f"Initial setup:\n{board}")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s", level=logging.DEBUG
    )
    main()
