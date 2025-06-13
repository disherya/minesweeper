"""Модуль с представлением(GUI) игры"""

__author__ = 'Шеряков Д.И.'

import tkinter as tk

from enums import Difficulty
from dataclasses_ import CellView


class MinesweeperView(tk.Tk):
    """Класс-представление игры сапёр"""

    def __init__(self) -> None:
        """Инициализация параметров"""
        super().__init__()
        self.option_add("*tearOff", False)

        self.board_view: list[list[CellView]] | None = None

        self.main_menu: tk.Menu = tk.Menu(self)

        self.file_menu: tk.Menu = self._create_file_menu()

        self.difficulty_radio: tk.StringVar = self._create_difficulty_radio_var()
        self.difficulty_menu: tk.Menu = self._create_difficulty_menu()

        self.help_menu: tk.Menu = self._create_help_menu()

        self._setting_up_gui()

    def _setting_up_gui(self) -> None:
        """Настройка GUI"""
        self.title('Сапёр')
        self.config(menu=self.main_menu)

        self.main_menu.add_cascade(label='Файл', menu=self.file_menu)
        self.main_menu.add_cascade(label='Сложность', menu=self.difficulty_menu)
        self.main_menu.add_cascade(label='Справка', menu=self.help_menu)

        self._place_window_center()

    def _create_file_menu(self) -> tk.Menu:
        """Создание меню Файл"""
        file_menu = tk.Menu(self.main_menu)

        file_menu.add_command(label='Новая игра')
        file_menu.add_separator()
        file_menu.add_command(label='Выход', command=lambda: self.destroy())

        return file_menu

    def _create_difficulty_menu(self) -> tk.Menu:
        """Создание меню Сложность"""
        difficulty_menu = tk.Menu(self.main_menu)

        difficulty_menu.add_radiobutton(label='Легко', variable=self.difficulty_radio, value=Difficulty.EASY)
        difficulty_menu.add_radiobutton(label='Нормально', variable=self.difficulty_radio, value=Difficulty.NORMAL)
        difficulty_menu.add_radiobutton(label='Сложно', variable=self.difficulty_radio, value=Difficulty.HARD)

        return difficulty_menu

    def _create_help_menu(self) -> tk.Menu:
        """Создание меню Справка"""
        help_menu = tk.Menu(self.main_menu)

        help_menu.add_command(label='О программе')

        return help_menu

    def _place_window_center(self, width: int = 300, height: int = 300) -> None:
        """
        Располагаем окно по центру

        Args:
            width: ширина окна
            height: высота окна
        """
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.geometry(f'{width}x{height}+{(screen_width - width) // 2}+{(screen_height - height) // 2}')

    @staticmethod
    def _create_difficulty_radio_var() -> tk.StringVar:
        """Создание радио переменной для меню Сложность"""
        diff_radio: tk.StringVar = tk.StringVar()
        diff_radio.set(Difficulty.EASY)

        return diff_radio

    def __call__(self):
        """Запуск графического интерфейса"""
        try:
            self.mainloop()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    gui = MinesweeperView()
    gui()
