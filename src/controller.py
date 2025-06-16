"""Модуль с контроллером игры"""

__author__ = 'Шеряков Д.И.'

from tkinter import Event, messagebox

from .model import MinesweeperModel
from .view import DIFFICULTY_MAPPING, MinesweeperView
from .enums import ActionType
from .dataclasses_ import CellView, Cell, MinesweeperResponse


class MinesweeperController:
    """Класс-контроллер игры сапёр"""

    def __init__(self) -> None:
        """Инициализация параметров"""
        self.view: MinesweeperView = MinesweeperView()
        self.model: MinesweeperModel = MinesweeperModel(*DIFFICULTY_MAPPING[self.view.difficulty_radio.get()])

    def __call__(self) -> None:
        self._add_commands_for_cells()
        self._add_commands_for_file_menu()
        self._add_commands_for_help_menu()

        self.view()

    def _add_commands_for_cells(self):
        """Добавляет команды для клеток(кнопок)"""
        for list_cells in self.view.board_view:
            for cell in list_cells:
                cell.bind(
                    '<ButtonPress-1>',
                    lambda e, r=cell.row, c=cell.col, action=ActionType.OPEN: self._cell_click(e, r, c, action)
                )
                cell.bind(
                    '<ButtonPress-3>',
                    lambda e, r=cell.row, c=cell.col, action=ActionType.MARK: self._cell_click(e, r, c, action)
                )

    def _cell_click(self, _event: Event, clicked_cell_row: int, clicked_cell_col: int, action_type: ActionType) -> None:
        """
        Метод вызываемый при нажатии кнопки

        Args:
            _event: событие
            clicked_cell_row: строка нажатой клетки
            clicked_cell_col: колонка нажатой клетки
            action_type: тип события
        """
        self.view.focus()

        minesweeper_response: MinesweeperResponse = self.model(clicked_cell_row, clicked_cell_col, action_type)

        self._update_board_gui(minesweeper_response)

        if minesweeper_response.is_win:
            messagebox.showinfo(title='Результат игры', message='Вы победили')
        elif minesweeper_response.is_gameover:
            messagebox.showinfo(title='Результат игры', message='Вы проиграли')

    def _update_board_gui(self, minesweeper_response: MinesweeperResponse) -> None:
        """
        Обновляет внешний вид игровой доски

        Args:
            minesweeper_response: ответ от модели
        """
        for list_gui_cells in self.view.board_view:
            for gui_cell in list_gui_cells:
                model_cell: Cell = minesweeper_response.board[gui_cell.row][gui_cell.col]

                text, disable = self._get_cell_text(model_cell)
                self._configurate_cell(gui_cell, text=text, disable=disable)

    def _add_commands_for_file_menu(self) -> None:
        """Добавляет команды для меню Файл"""
        self.view.file_menu.entryconfig('Новая игра', command=self._command_new_game)

    def _command_new_game(self) -> None:
        """Добавляет команду Новая игра"""
        self.view.relating_board()
        self.model: MinesweeperModel = MinesweeperModel(*DIFFICULTY_MAPPING[self.view.difficulty_radio.get()])
        self()

    def _add_commands_for_help_menu(self) -> None:
        """Добавляет команды для меню Справка"""
        self.view.help_menu.entryconfig('О программе', command=self._command_about)

    @staticmethod
    def _command_about() -> None:
        """Добавляет команду О программе"""
        messagebox.showinfo(
            title='О программе',
            message=
            '''
            Игра сапёр 
            Цель: открыть все клетки на поле, не содержащие мины
            
            При открытии клетки, если в ней нет мины,
            то показывается число, обозначающее количество мин в соседних клетках.
            Игроки используют эти числа, чтобы определить местонахождение мин и помечать их флажками.
            '''
        )

    @staticmethod
    def _configurate_cell(gui_cell: CellView, *, text: str = None, disable: bool = False) -> None:
        """
        Настраиваем клетку

        Args:
            gui_cell: gui клетка
            text: текст клетки
            disable: деактивировать ли клетку
        """
        gui_cell.config(text=text)

        if disable:
            gui_cell.config(state='disable')

    @staticmethod
    def _get_cell_text(model_cell: Cell) -> tuple[str, bool]:
        """
        Определяем текст для gui клетки

        Args:
            model_cell: клетка поля

        Returns:
            Текст для gui клетки
        """
        text: str = ' '
        disable: bool = False
        if model_cell.is_set_flag:
            text = '?'
        elif model_cell.is_revealed:
            disable = True
            if model_cell.is_mine:
                text = 'M'
            elif num_of_mines_around := model_cell.num_of_mines_around:
                text = str(num_of_mines_around)

        return text, disable
