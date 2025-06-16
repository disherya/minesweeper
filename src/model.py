"""Модуль с моделью игры"""

__author__ = 'Шеряков Д.И.'

from typing import Callable
from random import randint

from .dataclasses_ import Cell, MinesweeperResponse
from .enums import ActionType


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

        self._board: list[list[Cell]] = [[Cell() for _ in range(cols)] for _ in range(rows)]

        self._from_action_type_to_action: dict[str, Callable] = {
            ActionType.OPEN: self._open_cell,
            ActionType.MARK: self._mark_cell,
        }

        self._is_win: bool = False
        self._is_gameover: bool = False
        self._installed_markers: int = 0

        self._is_first_click: bool = True

        self._revealed_cells_after_click: list[Cell] = []

    def __call__(self, clicked_cell_row: int, clicked_cell_col: int, action_type: ActionType) -> MinesweeperResponse:
        """
        Игровой цикл

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
            action_type: тип события

        Returns:
            Ответ содержащий данные о текущем состоянии игры(победа?, поражение?, игровое поле)
        """
        action: Callable[[dict], None] = self._from_action_type_to_action[action_type]
        action(clicked_cell_row, clicked_cell_col)

        if self._is_first_click and action_type == ActionType.OPEN:
            self._preparing_board_after_first_click()

        if action_type == ActionType.OPEN:
            self._reveal_neighbours(clicked_cell_row, clicked_cell_col)
            self._check_game_result(clicked_cell_row, clicked_cell_col)

        self._revealed_cells_after_click = []

        return MinesweeperResponse(
            is_win=self._is_win,
            is_gameover=self._is_gameover,
            board=self._board,
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
        current_cell: Cell = self._board[clicked_cell_row][clicked_cell_col]
        if current_cell.is_mine or any([cell.is_mine for cell in self._revealed_cells_after_click]):
            self._is_gameover = True
            self._reveal_all_cells()
        elif self._check_win():
            self._is_gameover = True
            self._is_win = True
            self._reveal_all_cells()

    def _check_win(self) -> bool:
        """Проверка условия победы: кол-во закрытых клеток == кол-во мин"""
        unrevealed_cells: int = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if not self._board[row][col].is_revealed:
                    unrevealed_cells += 1

        return unrevealed_cells == self.mines

    def _open_cell(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """Открываем клетку"""
        current_cell: Cell = self._board[clicked_cell_row][clicked_cell_col]
        if not current_cell.is_set_flag and not current_cell.is_revealed:
            self._reveal_cell(current_cell)

    def _reveal_all_cells(self) -> None:
        """Помечает все клетки открытыми"""
        for row in range(self.rows):
            for col in range(self.cols):
                self._board[row][col].is_revealed = True
                self._board[row][col].is_set_flag = False

    def _mark_cell(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """
        Ставим или снимаем флаг с клетки

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
        """
        current_cell: Cell = self._board[clicked_cell_row][clicked_cell_col]

        if not current_cell.is_revealed and not self._is_first_click:
            current_cell.is_set_flag = not current_cell.is_set_flag

    def _reveal_neighbours(self, clicked_cell_row: int, clicked_cell_col: int) -> None:
        """
        Открываем соседние клетки по следующей схеме:
            - Если клетка не была нажата(попала в список нажатых сейчас), то раскрываем вокруг нажатой клетки и
                соседей соседей, если они без мин
            - Если клетка уже была нажата(не попала в список нажатых сейчас), то считаем кол-во флагов и мин вокруг.
                Если сходится, то окрываем даже мины, иначе ничего не делаем

        Args:
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: столбец нажатой клетки
        """
        neighbours: list[tuple[int, int]] = self._get_neighbours(clicked_cell_row, clicked_cell_col)
        stack: set[tuple[int, int]] = set(neighbours)

        if not self._revealed_cells_after_click:
            if self._check_marks_around_equal_mines_around(
                    self._board[clicked_cell_row][clicked_cell_col],
                    neighbours
            ):
                self._reveal_neighbours_impl(stack, True)
        else:
            self._reveal_neighbours_impl(stack)

    def _reveal_neighbours_impl(self, stack: set[tuple[int, int]], reveal_mines: bool = False) -> None:
        """
        В цикле обрабатываем каждого соседа. По условию раскрываем его. Если у соседа 0 мин вокруг, то добавляем его
            соседей в очередь на раскрытие.

        Args:
            stack: Множество с соседями
            reveal_mines: Раскрывать ли мины
        """
        while stack:
            current_row, current_col = stack.pop()
            current_cell: Cell = self._board[current_row][current_col]

            if (not current_cell.is_mine or reveal_mines) and not current_cell.is_revealed and not current_cell.is_set_flag:
                self._reveal_cell(current_cell)

                if current_cell.num_of_mines_around is not None and current_cell.num_of_mines_around == 0:
                    stack.update(self._get_neighbours(current_row, current_col))

    def _reveal_cell(self, cell: Cell) -> None:
        """
        Раскрытие клетки

        Args:
            cell: клетка
        """
        cell.is_revealed = True
        self._revealed_cells_after_click.append(cell)

    def _check_marks_around_equal_mines_around(self, clicked_cell: Cell, neighbours: list[tuple[int, int]]) -> bool:
        """
        Проверяет кол-во флагов и мин вокруг нажатой клетки

        Args:
            clicked_cell: нажатая клетка
            neighbours: соседи

        Returns:
            совпадает ли кол-во флагов и мин
        """
        num_of_marks_around: int = 0
        for n_row, n_col in neighbours:
            if self._board[n_row][n_col].is_set_flag:
                num_of_marks_around += 1

        return num_of_marks_around == clicked_cell.num_of_mines_around

    def _preparing_board_after_first_click(self):
        """Подготавливаем игровое поле после первого клика"""
        self._is_first_click = False
        self._place_mines()
        self._set_num_of_mines_around()

    def _place_mines(self) -> None:
        """Метод размещает мины на поле случайным образом исключая первую нажатую клетку"""
        placed_mines: int = 0
        while placed_mines < self.mines:
            current_cell: Cell = self._board[randint(0, self.rows - 1)][randint(0, self.cols - 1)]

            if not current_cell.is_mine and not current_cell.is_revealed:
                current_cell.is_mine = True
                placed_mines += 1

    def _set_num_of_mines_around(self) -> None:
        """Устанавливаем кол-во мин вокруг клетки в num_of_mines_around"""
        for row in range(self.rows):
            for col in range(self.cols):
                if not self._board[row][col].is_mine:
                    self._board[row][col].num_of_mines_around = self._get_num_of_mines(row, col)

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
            if self._board[n_row][n_col].is_mine:
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
