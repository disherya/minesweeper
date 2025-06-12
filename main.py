

from typing import Callable
from random import randint
from enum import StrEnum

from dataclasses import dataclass


class ActionType(StrEnum):
    """Типы действий"""
    OPEN = 'open'   # Открыть клетку
    MARK = 'mark'   # Пометить клетку флагом


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


class MinesweeperModel:
    """Класс игры сапёр"""

    def __init__(self, rows: int = 10, cols: int = 10, mines: int = 10) -> None:
        """
        Инициализация параметров

        Args:
            rows: Кол-во строк игрового поля
            cols: Кол-во столбцов игрового поля
            mines: Кол-во мин на игровом поле
        """
        self.rows: int = rows
        self.cols: int = cols
        self.mines: int = mines

        self.board: list[list[Cell]] = [[Cell() for _ in range(cols)] for _ in range(rows)]

        self._from_action_type_to_action: dict[str, Callable] = {
            ActionType.OPEN: self._open_cell,
            ActionType.MARK: self._mark_cell,
        }

        self.is_win: bool = False
        self.is_gameover: bool = False
        self._revealed_cells: int = 0

        self._is_first_click: bool = True

    def __call__(self, clicked_cell_row: int, clicked_cell_col: int, action_type: ActionType) -> MinesweeperResponse:
        """
        Игровой цикл

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
            action_type: тип события

        Returns:

        """
        if self._is_first_click:
            self._reveal_cell(clicked_cell_row, clicked_cell_col)
            self._preparing_board_after_first_click()

        action: Callable[[dict], None] = self._from_action_type_to_action[action_type]
        action(clicked_cell_row, clicked_cell_col)

        self._check_game_result(clicked_cell_row, clicked_cell_col)

        self._reveal_cell(clicked_cell_row, clicked_cell_col)

        return MinesweeperResponse(
            is_win=self.is_win,
            is_gameover=self.is_gameover,
            board=self.board,
        )

    def _check_game_result(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """
        Проверяем результат игры на текущий момент:
            - Проиграли, если попали на мину
            - Выиграли, если кол-во закрытых клеток == кол-во мин

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
        """
        current_cell: Cell = self.board[clicked_cell_row][clicked_cell_col]
        if current_cell.is_mine:
            print('Game Over')
            self.is_gameover = True
            self._reveal_all_cells()
        elif self.rows * self.cols - self._revealed_cells == self.mines:
            print('Win')
            self.is_gameover = True
            self.is_win = True
            self._reveal_all_cells()

    def _open_cell(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """Открываем клетку"""
        current_cell: Cell = self.board[clicked_cell_row][clicked_cell_col]
        if not current_cell.is_set_flag and not current_cell.is_revealed:
            current_cell.is_revealed = True
            self._revealed_cells += 1

    def _reveal_all_cells(self) -> None:
        """Помечает все клетки открытыми"""
        for row in range(self.rows):
            for col in range(self.cols):
                self.board[row][col].is_revealed = True
                self.board[row][col].is_set_flag = False

    def _mark_cell(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """
        Ставим или снимаем флаг с клетки

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
        """
        current_cell: Cell = self.board[clicked_cell_row][clicked_cell_col]
        if not current_cell.is_revealed:
            current_cell.is_set_flag = not current_cell.is_set_flag

    def _reveal_neighbours(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """
        Открываем соседние клетки, если на них нет мины.

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
        """
        stack: set[tuple[int, int]] = set(self._get_neighbours(clicked_cell_row, clicked_cell_col))

        while stack:
            current_row, current_col = stack.pop()
            current_cell: Cell = self.board[current_row][current_col]

            if not current_cell.is_mine and not current_cell.is_revealed and not current_cell.is_set_flag:
                current_cell.is_revealed = True

                if current_cell.num_of_mines_around and current_cell.num_of_mines_around == 0:
                    stack.update(self._get_neighbours(current_row, current_col))

    def _preparing_board_after_first_click(self):
        """Подготавливаем игровое поле после первого клика"""
        self._is_first_click = False
        self._place_mines()
        self._set_num_of_mines_around()

    def _reveal_cell(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """
        Помечает клету открытой

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
        """
        self.board[clicked_cell_row][clicked_cell_col].is_revealed = True

    def _place_mines(self) -> None:
        """Метод размещает мины на поле случайным образом исключая первую нажатую клетку"""
        placed_mines: int = 0
        while placed_mines < self.mines:
            current_cell: Cell = self.board[randint(0, self.rows - 1)][randint(0, self.cols - 1)]

            if not current_cell.is_mine and not current_cell.is_revealed:
                current_cell.is_mine = True
                placed_mines += 1

    def _set_num_of_mines_around(self) -> None:
        """Устанавливаем кол-во мин вокруг клетки в num_of_mines_around"""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.board[row][col].is_mine:
                    self.board[row][col].num_of_mines_around = self._get_num_of_mines(row, col)


    def _get_num_of_mines(self, row: int, col: int) -> int:
        """
        Получаем кол-во мин вокруг клетки

        Args:
            row: индекс строки
            col: индекс столбца

        Returns:
            Кол-во мин
        """
        mines: int = 0
        neighbours: list[tuple[int, int]] = self._get_neighbours(row, col)
        for n_row, n_col in neighbours:
            if self.board[n_row][n_col].is_mine:
                mines += 1

        return mines

    def _get_neighbours(self, row: int, col: int) -> list[tuple[int, int]]:
        """
        Возвращаем список кортежей координат соседних клеток по указанной клетке

        Args:
            row: индекс строки
            col: индекс столбца

        Returns:
            Список из кортежей (индекс_строки, индекс_столбца)
        """
        min_row, max_row, min_col, max_col = self._determine_area_of_neighbors(row, col)

        neighbours: list[tuple[int, int]] = []
        for row_ in range(min_row, max_row + 1):
            for col_ in range(min_col, max_col + 1):
                neighbour_row_col = (row_, col_)
                if neighbour_row_col != (row, col):
                    neighbours.append(neighbour_row_col)

        return neighbours

    def _determine_area_of_neighbors(self, row: int, col: int) -> tuple[int, int, int, int]:
        """
        Определяем область поиска соседей вокруг клетки

        Args:
            row: индекс строки
            col: индекс столбца

        Returns:
            Кортеж из значений: начальная строка, конечная строка, начальный столбец, конечный столбец
        """
        min_row = row - 1 if row > 0 else 0
        max_row = row + 1 if row < self.rows - 1 else self.rows - 1
        min_col = col - 1 if col > 0 else 0
        max_col = col + 1 if col < self.cols - 1 else self.cols - 1

        return min_row, max_row, min_col, max_col
