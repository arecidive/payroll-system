import sqlite3

from models.database import DatabaseManager
from models.employee import Employee
from models.work_type import WorkType


class PayrollDepartment:
    """Класс представляет собой отдел расчета зарплат."""

    _instance = None

    def __new__(cls, *args, **kwargs) -> "PayrollDepartment":
        """Создание единственного экземпляра класса."""
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, *kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.employees = {}
        self.work_rates = {}
        self.db_manager = DatabaseManager()
        self._load_data()

    def _load_data(self) -> None:
        """Загрузка данных из БД при инициализации."""
        try:
            self.work_rates = self.db_manager.get_all_work_rates()
            employee_names = self.db_manager.get_all_employees()
            for name in employee_names:
                self.employees[name] = Employee(name=name, db_manager=self.db_manager)

        except sqlite3.Error as e:
            print(f"Ошибка при загрузке данных из БД: {e}")

    def add_employee(self, name: str) -> None:
        """Создание работника в БД отдела расчета зарплат."""
        if not name or not (2 <= len(name) <= 100):
            raise ValueError(f"Имя сотрудника не должно быть пустым и должно быть от 2 до 100 символов")
        if name in self.employees:
            raise ValueError(f"Сотрудник '{name}' уже существует")
        self.db_manager.add_employee(name)
        self.employees.update({name: Employee(name, self.db_manager)})

    def delete_employee(self, name: str) -> None:
        """Удаление работника в БД отдела расчета зарплат."""
        if name not in self.employees:
            raise KeyError(f"Сотрудник '{name}' не существует")
        self.db_manager.delete_employee(name)
        self.employees.pop(name)

    def add_work_rate(self, work_type: WorkType, rate: float) -> None:
        """Изменение часовой ставки за определенный тип работы."""
        if not rate or not (0 < rate < 1_000_000):
            raise ValueError("Ставка должна быть положительным числом и меньше 1.000.000")
        self.db_manager.add_work_rate(work_type, rate)
        self.work_rates[work_type] = rate

    def add_work(self, name: str, work_type: WorkType, hours: float) -> None:
        """Добавление работы сотруднику."""
        if name not in self.employees:
            raise KeyError(f"Сотрудника '{name}' не существует")
        if not hours or not (0 < hours < 1_000):
            raise ValueError("Количество часов должно быть положительным числом и меньше 1.000")
        if work_type not in self.work_rates:
            raise ValueError(f"Добавьте ставку для '{work_type}'")
        self.employees[name].add_work(work_type, hours)

    def get_employee_salary(self, name: str) -> float:
        """Вычисление зарплаты определенного сотрудника."""
        return self.employees[name].calculate_salary(self.work_rates) if name in self.employees else 0

    def get_total_payroll(self) -> float:
        """Вычисление зарплат всех сотрудников."""
        return sum(employee.calculate_salary(self.work_rates) for employee in self.employees.values())

    def clear_all_employees(self) -> None:
        """Удаление всех сотрудников из системы и БД, сохраняя ставки."""
        self.db_manager.clear_employees_and_works()
        self.employees.clear()

    def clear_data(self) -> None:
        """Очистка всех данных."""
        self.db_manager.clear_database()
        self.employees.clear()
        self.work_rates.clear()
