"""Модуль с перечислениями"""

__author__ = 'Шеряков Д.И.'

from enum import StrEnum


class ActionType(StrEnum):
    """Типы действий"""
    OPEN = 'open'   # Открыть клетку
    MARK = 'mark'   # Пометить клетку флагом


class Difficulty(StrEnum):
    """Уровни сложности"""
    EASY = 'easy'
    NORMAL = 'normal'
    HARD = 'hard'
