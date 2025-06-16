"""Модуль запуска игры"""

__author__ = 'Шеряков Д.И.'

from src.controller import MinesweeperController


if __name__ == '__main__':
    controller = MinesweeperController()
    controller()
