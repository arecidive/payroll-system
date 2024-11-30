from enum import Enum


class WorkType(Enum):
    """Класс - перечисление разных типов работы."""
    REGULAR = 1  # обычный
    OVERTIME = 2  # переработка
    WEEKEND = 3  # выходной
