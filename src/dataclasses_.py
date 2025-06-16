"""Модуль с датаклассами"""

__author__ = 'Шеряков Д.И.'

from tkinter import ttk

from dataclasses import dataclass, InitVar


@dataclass
class CellView(ttk.Button):
    """Rласс-представление одной клетки поля"""
    master: InitVar[ttk.Frame]
    row: int
    col: int

    def __post_init__(self, master):
        super().__init__(master=master, text=' ', width=2)
        self.grid(row=self.row, column=self.col)


@dataclass
class Cell:
    """Класс клетки поля"""
    is_mine: bool = False
    is_revealed: bool = False
    is_set_flag: bool = False
    num_of_mines_around: int | None = None


@dataclass
class MinesweeperResponse:
    """Класс ответа после клика на клетку"""
    is_win: bool
    is_gameover: bool
    board: list[list[Cell]]
