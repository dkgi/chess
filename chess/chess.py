# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import annotations
import logging
import abc
import re
from enum import Enum
from typing import Tuple
from typing_extensions import Final

LOG: logging.Logger = logging.getLogger(__file__)


class Color(Enum):
    BLACK = 0
    WHITE = 1

    def __str__(self) -> str:
        if self == Color.BLACK:
            return "black"
        else:
            return "white"


class Figure:
    def __init__(self, color: Color) -> None:
        self.color: Final[Color] = color

    def __str__(self) -> str:
        color = "\033[30m" if self.color == Color.BLACK else "\033[37m"
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


class InvalidPosition(Exception):
    pass


class Position:
    def __init__(self, row: int, column: int) -> None:
        # Rows: 1, 2, 3, ...
        # Columns: A, B, C, ...
        self.row: Final[int] = row
        self.column: Final[int] = column

    @classmethod
    def parse(cls, input: str) -> Position:
        match = re.match(r"^([a-h])([1-8])$", input)
        if match is None:
            raise InvalidPosition(f"`{input}` is not a valid field, e.g. A1")

        return Position(
            ord(match.groups(0)[1]) - ord("1"), ord(match.groups(0)[0]) - ord("a")
        )

    def __str__(self) -> str:
        return f"{chr(self.column + ord('A'))}{chr(self.row + ord('1'))}"


class InvalidMove(Exception):
    pass


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
                color = dark if (row_index + field_index) % 2 == 0 else light
                line += f"{color}{field or ' '}{clear}"
            lines.append(line)

        return "\n".join(reversed(lines))

    def move(self, *, color: Color, from_: Position, to: Position) -> None:
        field = self._fields[from_.row][from_.column]
        if field is None or field.color != color:
            raise InvalidMove(f"No {color} piece at {from_}")

        # TODO: actual validation if move is valid
        self._fields[to.row][to.column] = field
        self._fields[from_.row][from_.column] = None


class Game:
    def __init__(self) -> None:
        self._board: Board = Board()
        self._turn = Color.WHITE

    def show_board(self) -> None:
        print(f"{self._board}")
        color = "White" if self._turn == Color.WHITE else "Black"
        print(f"{color}'s turn.")

    def move(self, *, from_: Position, to: Position) -> None:
        try:
            self._board.move(color=self._turn, from_=from_, to=to)
            self._turn = Color.WHITE if self._turn == Color.BLACK else Color.BLACK
            self.show_board()
        except InvalidMove as error:
            print(f"Invalid move: {error}")


HELP = """\
Available commands:
    new: start a new game

    help: show this message
    exit: leave the program\

    move <L> <L>: move a piece. `L` is in coordinate notation.
                  E.g. `move E2 E4` will advance a pawn two fields.
"""


class InvalidCommand(Exception):
    def __init__(self, command: str, message: str | None = None) -> None:
        self._command = command
        self._message = message

    def __str__(self) -> str:
        if self._message is not None:
            return f"{self._command} ({self._message})"
        return f"{self._command}"


def main() -> None:
    print("Chess 0.1. Type `help` for instructions.")
    game = None
    while True:
        try:
            command = input(">> ").lower()

            if command == "exit":
                print("Exiting...")
                break

            if command == "help":
                print(HELP)
                continue

            if command == "new":
                game = Game()
                game.show_board()
                continue

            if command == "debug":
                import pdb

                pdb.set_trace()

            if command.startswith("move "):
                if game is None:
                    raise InvalidCommand(
                        command, "No game in progress, start game with `new`."
                    )
                parts = command.split()
                if len(parts) != 3:
                    raise InvalidCommand(command)

                try:
                    game.move(
                        from_=Position.parse(parts[1]), to=Position.parse(parts[2])
                    )
                except InvalidPosition as error:
                    raise InvalidCommand(command, str(error))
                continue

            raise InvalidCommand(command)
        except InvalidCommand as error:
            print(f"Invalid command: {error}\nEnter `help` for instructions.")
            continue
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    main()
