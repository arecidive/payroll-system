from abc import ABC, abstractmethod

from models.work_type import WorkType


class SalaryCalculationStrategy(ABC):
    """Абстрактный класс для стратегии расчета зарплаты."""

    @abstractmethod
    def calculate(self, works: list[dict[WorkType, float]], rates: dict[WorkType, float]) -> float:
        """Расчет зарплаты по конкретной стратегии."""
        pass


class StandardSalaryStrategy(SalaryCalculationStrategy):
    """Стандартная стратегия расчета зарплаты."""

    def calculate(self, works: list[dict[WorkType, float]], rates: dict[WorkType, float]) -> float:
        return sum(hours * rates[work_type] for work in works for work_type, hours in work.items())


class OvertimeBonusStrategy(SalaryCalculationStrategy):
    """Стратегия расчета зарплаты с повышенной ставкой за переработку."""

    def calculate(self, works: list[dict[WorkType, float]], rates: dict[WorkType, float]) -> float:
        total = 0
        for work in works:
            for work_type, hours in work.items():
                rate = rates[work_type]
                if work_type == WorkType.OVERTIME:
                    total += hours * rate * 1.5
                else:
                    total += hours * rate
        return total
