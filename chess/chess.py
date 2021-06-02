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

class Rook(Figure):
    def name(self) -> str:
        return "R"

class King(Figure):
    def name(self) -> str:
        return "K"

class Queen(Figure):
    def name(self) -> str:
        return "Q"

class Knight(Figure):
    def name(self) -> str:
        return "N"

class Bishop(Figure):
    def name(self) -> str:
        return "B"

class Board:
    def __init__(self) -> None:
        # self._fields[1][a] is bottom left, self._fields[1][h] is bottom right
        self._fields: list[list[Figure | None]] = []
        for row_index in range(8):
            self._fields.append([None] * 8)

        self._fields[0][4] = King(Color.WHITE)
        self._fields[7][4] = King(Color.BLACK)

        self._fields[0][3] = Queen(Color.WHITE)
        self._fields[7][3] = Queen(Color.BLACK)

        self._fields[0][2] = Bishop(Color.WHITE)
        self._fields[7][2] = Bishop(Color.BLACK)
        self._fields[0][5] = Bishop(Color.WHITE)
        self._fields[7][5] = Bishop(Color.BLACK)

        self._fields[0][1] = Knight(Color.WHITE)
        self._fields[7][1] = Knight(Color.BLACK)
        self._fields[0][6] = Knight(Color.WHITE)
        self._fields[7][6] = Knight(Color.BLACK)

        self._fields[0][0] = Rook(Color.WHITE)
        self._fields[7][0] = Rook(Color.BLACK)
        self._fields[0][7] = Rook(Color.WHITE)
        self._fields[7][7] = Rook(Color.BLACK)

        self._fields[1] = [Pawn(Color.WHITE)] * 8
        self._fields[6] = [Pawn(Color.BLACK)] * 8

    def __str__(self) -> str:
        light = "\u001b[42m"
        dark = "\u001b[43m"
        clear = "\033[0m"

        lines = ["  ABCDEFGH"]

        for row_index, row in enumerate(self._fields):
            line = f"{row_index + 1} "
            for field_index, field in enumerate(row):
                color = (
                    dark if (row_index + field_index) % 2 == 0 else light
                )
                line += f"{color}{field or ' '}{clear}"
            lines.append(line)

        return "\n".join(reversed(lines))


def main() -> None:
    board = Board()
    LOG.info(f"Initial setup:\n{board}")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s", level=logging.DEBUG
    )
    main()
