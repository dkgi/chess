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

    def inverse(self) -> Color:
        if self == Color.BLACK:
            return Color.WHITE
        else:
            return Color.BLACK


class Field:
    def __init__(self, color: Color | None) -> None:
        self.color: Final[Color | None] = color

    def __str__(self) -> str:
        if self.color is None:
            return " "

        color = "\033[30m" if self.color == Color.BLACK else "\033[37m"
        return f"{color}{self.name()}\033[0m"

    def is_empty(self) -> bool:
        return self.color == None

    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def can_move_to(self, board: Board, from_: Position) -> list[Position]:
        return []


class Empty(Field):
    def __init__(self) -> None:
        super().__init__(color=None)

    def can_move_to(self, board: Board, from_: Position) -> list[Position]:
        return []


class Pawn(Field):
    def name(self) -> str:
        return "P"

    def can_move_to(self, board: Board, from_: Position) -> list[Position]:
        candidates = []

        direction = 1 if self.color == Color.WHITE else -1

        # Forward
        advance_one = from_.translate(row_offset=direction)
        if advance_one is not None and board[advance_one].is_empty():
            candidates.append(advance_one)

            if (self.color == Color.WHITE and from_.row == 1) or (
                self.color == Color.BLACK and from_.row == 6
            ):
                advance_two = advance_one.translate(row_offset=direction)
                if advance_two is not None and board[advance_two].is_empty():
                    candidates.append(advance_two)

        # Strike
        advance_left = from_.translate(row_offset=direction, column_offset=-1)
        if (
            advance_left is not None
            and board[advance_left].color == self.color.inverse()
        ):
            candidates.append(advance_left)

        advance_right = from_.translate(row_offset=direction, column_offset=1)
        if (
            advance_right is not None
            and board[advance_right].color == self.color.inverse()
        ):
            candidates.append(advance_right)

        # En passant
        # TODO: not implemented

        # Queen conversion
        # TODO: not implemented

        return candidates


class Rook(Field):
    def name(self) -> str:
        return "R"


class King(Field):
    def name(self) -> str:
        return "K"


class Queen(Field):
    def name(self) -> str:
        return "Q"


class Knight(Field):
    def name(self) -> str:
        return "N"


class Bishop(Field):
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False

        return self.row == other.row and self.column == other.column

    def translate(
        self, *, row_offset: int | None = 0, column_offset: int | None = 0
    ) -> Position | None:
        row = self.row + row_offset
        column = self.column + column_offset

        if row in range(8) and column in range(8):
            return Position(row, column)

        return None


class InvalidMove(Exception):
    pass


class Board:
    def __init__(self) -> None:
        # self._board[1][a] is bottom left, self._board[1][h] is bottom right
        self._board: list[list[Field]] = []
        for row_index in range(8):
            self._board.append([Empty()] * 8)

        self._board[0][4] = King(Color.WHITE)
        self._board[7][4] = King(Color.BLACK)

        self._board[0][3] = Queen(Color.WHITE)
        self._board[7][3] = Queen(Color.BLACK)

        self._board[0][2] = Bishop(Color.WHITE)
        self._board[7][2] = Bishop(Color.BLACK)
        self._board[0][5] = Bishop(Color.WHITE)
        self._board[7][5] = Bishop(Color.BLACK)

        self._board[0][1] = Knight(Color.WHITE)
        self._board[7][1] = Knight(Color.BLACK)
        self._board[0][6] = Knight(Color.WHITE)
        self._board[7][6] = Knight(Color.BLACK)

        self._board[0][0] = Rook(Color.WHITE)
        self._board[7][0] = Rook(Color.BLACK)
        self._board[0][7] = Rook(Color.WHITE)
        self._board[7][7] = Rook(Color.BLACK)

        self._board[1] = [Pawn(Color.WHITE)] * 8
        self._board[6] = [Pawn(Color.BLACK)] * 8

    def __str__(self) -> str:
        light = "\u001b[42m"
        dark = "\u001b[43m"
        clear = "\033[0m"

        lines = ["  ABCDEFGH"]

        for row_index, row in enumerate(self._board):
            line = f"{row_index + 1} "
            for field_index, field in enumerate(row):
                color = dark if (row_index + field_index) % 2 == 0 else light
                line += f"{color}{field or ' '}{clear}"
            lines.append(line)

        return "\n".join(reversed(lines))

    def __getitem__(self, key: Position) -> Field:
        return self._board[key.row][key.column]

    def __setitem__(self, key: Position, value: Field) -> None:
        self._board[key.row][key.column] = value

    def move(self, *, moving_color: Color, from_: Position, to: Position) -> None:
        field = self[from_]

        if field.color != moving_color:
            raise InvalidMove(f"no {color} piece at {from_}")

        if self[to].color == moving_color:
            raise InvalidMove(f"cannot move to field with {moving_color} piece")

        if to not in field.can_move_to(self, from_):
            raise InvalidMove(f"{field} cannot move from {from_} to {to}")

        if self[to].color not in [moving_color, None]:
            LOG.info(f"{self[from_]} at {from_} strikes {self[to]} at {to}")

        self[to] = field
        self[from_] = Empty()


class Game:
    def __init__(self) -> None:
        self._board: Board = Board()
        self._turn = Color.WHITE

    def __str__(self) -> str:
        color = "White" if self._turn == Color.WHITE else "Black"
        return f"{self._board}\n{color}'s turn."

    def move(self, *, from_: Position, to: Position) -> None:
        try:
            self._board.move(moving_color=self._turn, from_=from_, to=to)
            self._turn = self._turn.inverse()
            LOG.info(f"{self}")
        except InvalidMove as error:
            LOG.error(f"Invalid move: {error}")


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
    LOG.info("Chess 0.1. Type `help` for instructions.")
    game = None
    while True:
        try:
            command = input(">> ").lower()

            if command == "exit":
                LOG.info("Exiting...")
                break

            if command == "help":
                LOG.info(HELP)
                continue

            if command == "new":
                game = Game()
                LOG.info(f"{game}")
                continue

            if command == "debug":
                import pdb

                pdb.set_trace()

            if command.startswith("m ") or command.startswith("move "):
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
            LOG.info(f"Invalid command: {error}\nEnter `help` for instructions.")
            continue
        except KeyboardInterrupt:
            LOG.info("\nExiting...")
            break


if __name__ == "__main__":
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    main()
