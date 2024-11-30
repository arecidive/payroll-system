from models.employee import Employee
from models.work_type import WorkType


class PayrollDepartment:
    """Класс представляет собой отдел расчета зарплат."""

    _instance = None

    def __new__(cls, *args, **kwargs) -> 'PayrollDepartment':
        """Создание единственного экземпляра класса."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, *kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.employees = {}
        self.work_rates = {}

    def add_employee(self, name: str) -> None:
        """Создание работника в БД отдела расчета зарплат."""
        if not name or not (2 <= len(name) <= 100):
            raise ValueError(f"Имя сотрудника не должно быть пустым и должно быть от 2 до 100 символов")
        if name in self.employees:
            raise ValueError(f"Сотрудник '{name}' уже существует")
        return self.employees.update({name: Employee(name)})

    def delete_employee(self, name: str) -> None:
        """Удаление работника в БД отдела расчета зарплат."""
        self.employees.pop(name)

    def add_work_rate(self, work_type: WorkType, rate: float) -> None:
        """Изменение часовой ставки за определенный тип работы."""
        if not rate or not (0 < rate < 1_0000_000):
            raise ValueError("Ставка должна быть положительным числом и меньше 1.000.000")
        self.work_rates[work_type] = rate

    def add_work(self, name: str, work_type: WorkType, hours: float) -> None:
        """Добавление работы сотруднику."""
        if name not in self.employees:
            raise KeyError(f"Сотрудника '{name}' не существует")
        if not hours or not (0 < hours < 1_000):
            raise ValueError("Количество часов должно быть положительным числом и меньше 1.000")
        return self.employees[name].add_work(work_type, hours)

    def get_employee_salary(self, name: str) -> float:
        """Вычисление зарплаты определенного сотрудника."""
        if name in self.employees:
            return self.employees[name].calculate_salary(self.work_rates)
        return 0

    def get_total_payroll(self) -> float:
        """Вычисление зарплат всех сотрудников."""
        return sum(
            employee.calculate_salary(self.work_rates)
            for employee in self.employees.values()
        )
