"""Модуль для тестирования модели игры"""

__author__ = 'Шеряков'

import pytest

from src.model import MinesweeperModel
from src.dataclasses_ import Cell


@pytest.mark.parametrize(
    'c_row, c_col, lose, reveal',
    [
        (0, 0, True, True),
        (1, 1, False, False),
    ]
)
def test_check_game_result(c_row, c_col, lose, reveal):
    # Arrange
    model = MinesweeperModel(3, 3, 3)
    model._board[0][0].is_mine = True

    # Act
    model._check_game_result(c_row, c_col)

    # Assert
    assert model._is_gameover == lose
    assert model._is_win == False

    for list_of_cell in model._board:
        for cell in list_of_cell:
            assert cell.is_revealed == reveal


def test_check_game_result_lose():
    # Arrange
    model = MinesweeperModel(3, 3, 3)
    model._board[0][0].is_mine = True
    model._revealed_cells_after_click.append(Cell(is_mine=True))

    # Act
    model._check_game_result(1, 1)

    # Assert
    assert model._is_gameover == True
    assert model._is_win == False

    for list_of_cell in model._board:
        for cell in list_of_cell:
            assert cell.is_revealed == True


def test_check_game_result_win():
    # Arrange
    model = MinesweeperModel(3, 3, 1)
    for list_of_cell in model._board:
        for cell in list_of_cell:
            cell.is_revealed = True

    model._board[0][0].is_mine = True
    model._board[0][0].is_revealed = False

    # Act
    model._check_game_result(1, 1)

    # Assert
    assert model._is_gameover == True
    assert model._is_win == True

    for list_of_cell in model._board:
        for cell in list_of_cell:
            assert cell.is_revealed == True


@pytest.mark.parametrize(
    'closed, exp_result',
    [
        (1, True),
        (2, False)
    ]
)
def test_check_win(closed, exp_result):
    # Arrange
    model = MinesweeperModel(3, 3, 1)
    for list_of_cell in model._board:
        for cell in list_of_cell:
            cell.is_revealed = True

    model._board[0][0].is_mine = True
    for i in range(closed):
        model._board[0][i].is_revealed = False

    # Act
    result = model._check_win()

    # Assert
    assert result == exp_result


@pytest.mark.parametrize(
    'is_flag, is_revealed, exp_reveal, len_of_clicked',
    [
        (False, False, True, 1),
        (True, False, False, 0),
        (False, True, True, 0),
    ]
)
def test_open_cell(is_flag, is_revealed, exp_reveal, len_of_clicked):
    # Arrange
    model = MinesweeperModel(3, 3, 1)

    cell = model._board[0][0]
    if is_flag:
        cell.is_set_flag = True
    if is_revealed:
        cell.is_revealed = True

    # Act
    model._open_cell(0, 0)

    # Assert
    assert cell.is_revealed == exp_reveal
    assert len(model._revealed_cells_after_click) == len_of_clicked


def test_reveal_all_cells():
    # Arrange
    model = MinesweeperModel(3, 3, 1)

    # Act
    model._reveal_all_cells()

    # Assert
    for list_of_cell in model._board:
        for cell in list_of_cell:
            assert cell.is_revealed == True


@pytest.mark.parametrize(
    'is_set_flag, is_revealed, is_first_click, exp_res',
    [
        (False, False, False, True),
        (False, False, True, False),
        (True, False, False, False),
        (False, True, False, False),
    ]
)
def test_mark_cell(is_set_flag, is_revealed, is_first_click, exp_res):
    # Arrange
    model = MinesweeperModel(3, 3, 1)

    cell = model._board[0][0]
    cell.is_set_flag = is_set_flag
    cell.is_revealed = is_revealed
    model._is_first_click = is_first_click

    # Act
    model._mark_cell(0, 0)

    # Assert
    assert cell.is_set_flag == exp_res

@pytest.mark.parametrize(
    'is_mine, not_revealed',
    [
        (False, 0),
        (True, 1),

    ]
)
def test_reveal_neighbours(is_mine, not_revealed):
    # Arrange
    model = MinesweeperModel(3, 3, 3)

    model._board[0][0].is_mine = is_mine
    model._board[1][1].is_revealed = True
    model._revealed_cells_after_click.append(model._board[1][1])

    # Act
    model._reveal_neighbours(1, 1)

    # Assert
    _not_revealed = 0
    for list_of_cell in model._board:
        for cell in list_of_cell:
            if not cell.is_revealed:
                _not_revealed += 1

    assert _not_revealed == not_revealed


def test_reveal_neighbours_with_mark():
    # Arrange
    model = MinesweeperModel(3, 3, 1)

    for list_of_cell in model._board:
        for cell in list_of_cell:
            cell.num_of_mines_around = 0

    model._board[0][0].is_revealed = True
    model._board[0][0].num_of_mines_around = 1
    model._board[0][1].is_mine = True
    model._board[0][1].is_set_flag = True

    # Act
    model._reveal_neighbours(0, 0)

    # Assert
    _not_revealed = 0
    for list_of_cell in model._board:
        for cell in list_of_cell:
            if not cell.is_revealed:
                _not_revealed += 1

    assert _not_revealed == 1


@pytest.mark.parametrize(
    'reveal_mines, not_revealed',
    [
        (False, 1),
        (True, 0),
    ]
)
def test_reveal_neighbours_impl(reveal_mines, not_revealed):
    # Arrange
    model = MinesweeperModel(3, 3, 1)
    model._board[0][1].is_mine = True
    model._board[1][1].is_revealed = True

    stack = set()

    for i, list_of_mines in enumerate(model._board):
        for j, cell in enumerate(list_of_mines):
            stack.add((i, j))
    stack.remove((1, 1))

    # Act
    model._reveal_neighbours_impl(stack, reveal_mines)

    # Assert
    _not_revealed = 0
    for list_of_cell in model._board:
        for cell in list_of_cell:
            print(cell.is_revealed)
            if not cell.is_revealed:
                _not_revealed += 1

    assert _not_revealed == not_revealed


def test_reveal_cell():
    # Arrange
    model = MinesweeperModel(3, 3, 1)

    cell = model._board[1][1]

    # Act
    model._reveal_cell(cell)

    # Assert
    assert cell.is_revealed == True
    assert len(model._revealed_cells_after_click) == 1


@pytest.mark.parametrize(
    'is_set_flag, exp_res',
    [
        (False, False),
        (True, True),
    ]
)
def test_check_marks_around_equal_mines_around(is_set_flag, exp_res):
    # Arrange
    model = MinesweeperModel(3, 3, 1)

    clicked_cell = model._board[1][1]
    clicked_cell.num_of_mines_around = 1

    model._board[0][0].is_set_flag = is_set_flag

    neighbours = []

    for i, list_of_mines in enumerate(model._board):
        for j, cell in enumerate(list_of_mines):
            neighbours.append((i, j))
    neighbours.remove((1, 1))

    # Act
    result = model._check_marks_around_equal_mines_around(clicked_cell, neighbours)

    # Assert
    assert result == exp_res


def test_preparing_board_after_first_click():
    # Arrange
    model = MinesweeperModel(3, 3, 3)

    # Act
    model._preparing_board_after_first_click()

    # Assert
    assert model._is_first_click == False

    num_of_mines = 0
    for list_of_cell in model._board:
        for cell in list_of_cell:
            if cell.is_mine:
                num_of_mines += 1

    assert num_of_mines == model.mines


def test_place_mines():
    # Arrange
    model = MinesweeperModel(3, 3, 3)

    # Act
    model._place_mines()

    # Assert
    num_of_mines = 0
    for list_of_cell in model._board:
        for cell in list_of_cell:
            if cell.is_mine:
                num_of_mines += 1

    assert num_of_mines == model.mines


def test_set_num_of_mines_around():
    # Arrange
    model = MinesweeperModel(3, 3, 2)
    model._board[1][0].is_mine = True
    model._board[0][2].is_mine = True

    # Act
    model._set_num_of_mines_around()

    # Assert
    assert model._board[0][0].num_of_mines_around == 1
    assert model._board[0][1].num_of_mines_around == 2
    assert model._board[0][2].num_of_mines_around is None
    assert model._board[1][0].num_of_mines_around is None
    assert model._board[1][1].num_of_mines_around == 2
    assert model._board[1][2].num_of_mines_around == 1
    assert model._board[2][0].num_of_mines_around == 1
    assert model._board[2][1].num_of_mines_around == 1
    assert model._board[2][2].num_of_mines_around == 0


@pytest.mark.parametrize(
    'row, col, exp_res',
    [
        (1, 1, 2),
        (0, 0, 1),
        (2, 2, 0),
    ]
)
def test_get_num_of_mines(row, col, exp_res):
    # Arrange
    model = MinesweeperModel(3, 3, 2)
    model._board[1][0].is_mine = True
    model._board[0][2].is_mine = True

    # Act
    result = model._get_num_of_mines(row, col)

    # Assert
    assert result == exp_res


def test_get_neighbours():
    # Arrange
    model = MinesweeperModel(5, 5, 2)

    # Act
    neighbours = model._get_neighbours(2, 2)

    # Assert
    assert len(neighbours) == 8


@pytest.mark.parametrize(
    'row, col, exp_min_r, exp_max_r, exp_min_c, exp_max_c',
    [
        (0, 0, 0, 1, 0, 1),
        (0, 2, 0, 1, 1, 3),
        (0, 4, 0, 1, 3, 4),
        (2, 0, 1, 3, 0, 1),
        (4, 0, 3, 4, 0, 1),
        (4, 2, 3, 4, 1, 3),
        (4, 4, 3, 4, 3, 4),
        (2, 2, 1, 3, 1, 3),
    ]
)
def test_determine_area_of_neighbors(row, col, exp_min_r, exp_max_r, exp_min_c, exp_max_c):
    # Arrange
    model = MinesweeperModel(5, 5, 2)

    # Act
    min_row, max_row, min_col, max_col = model._determine_area_of_neighbors(row, col)

    # Assert
    assert min_row == exp_min_r
    assert max_row == exp_max_r
    assert min_col == exp_min_c
    assert max_col == exp_max_c
