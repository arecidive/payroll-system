from models.database import DatabaseManager
from models.work_type import WorkType
from models.salary_strategy import SalaryCalculationStrategy, StandardSalaryStrategy


class Employee:
    """Класс представляет собой сотрудника."""

    def __init__(
        self,
        name: str,
        db_manager: DatabaseManager,
        salary_strategy: SalaryCalculationStrategy = StandardSalaryStrategy(),
    ) -> None:
        self.name = name
        self.works = db_manager.get_employee_works(name)
        self.db_manager = db_manager
        self.salary_strategy = salary_strategy

    def add_work(self, work_type: WorkType, hours: float) -> None:
        """Добавление работы сотруднику."""
        self.db_manager.add_work(self.name, work_type, hours)
        self.works.append({work_type: hours})

    def calculate_salary(self, rates: dict[WorkType, float]) -> float:
        """Расчет зарплаты сотрудника."""
        return self.salary_strategy.calculate(self.works, rates)

    def set_salary_strategy(self, strategy: SalaryCalculationStrategy) -> None:
        """Установление стратегии по расчету зарплаты."""
        self.salary_strategy = strategy
