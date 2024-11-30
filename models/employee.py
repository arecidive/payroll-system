from models.work_type import WorkType
from models.salary_strategy import SalaryCalculationStrategy, StandardSalaryStrategy


class Employee:
    """Класс представляет собой сотрудника."""

    def __init__(
        self,
        name: str,
        salary_strategy: SalaryCalculationStrategy = StandardSalaryStrategy(),
    ) -> None:
        self.name = name
        self.works = []
        self.salary_strategy = salary_strategy

    def add_work(self, work_type: WorkType, hours: float) -> None:
        """Добавление работы сотруднику."""
        self.works.append({work_type: hours})

    def calculate_salary(self, rates: dict[WorkType, float]) -> float:
        """Расчет зарплаты сотрудника."""
        return self.salary_strategy.calculate(self.works, rates)

    def set_salary_strategy(self, strategy: SalaryCalculationStrategy) -> None:
        """Установление стратегии по расчету зарплаты."""
        self.salary_strategy = strategy
