import sqlite3

from models.work_type import WorkType


class DatabaseManager:
    """Класс для работы с базой данных (Singleton)."""

    _instance = None

    def __new__(cls, *args, **kwargs) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name: str = "payroll.db") -> None:
        if not self._initialized:
            self.db_name = db_name
            self._init_db()
            self._initialized = True

    def _init_db(self) -> None:
        """Инициализация базы данных."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_rates (
                    work_type TEXT PRIMARY KEY,
                    rate REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS works (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    work_type TEXT,
                    hours REAL,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                )
            """)
            conn.commit()

    def add_employee(self, name: str) -> None:
        """Добавление сотрудника в БД."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (name) VALUES (?)", (name,))
            conn.commit()

    def add_work_rate(self, work_type: WorkType, rate: float) -> None:
        """Добавление/обновление ставки за работу."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO work_rates (work_type, rate) VALUES (?, ?)",
                (work_type.name, rate)
            )
            conn.commit()

    def add_work(self, name: str, work_type: WorkType, hours: float) -> None:
        """Добавление работы сотруднику."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM employees WHERE name = ?", (name,))
            employee_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO works (employee_id, work_type, hours) VALUES (?, ?, ?)",
                (employee_id, work_type.name, hours)
            )
            conn.commit()

    def get_employee_works(self, name: str) -> list[dict[WorkType, float]]:
        """Получение работ конкретного сотрудника."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT w.work_type, w.hours 
                FROM works w
                JOIN employees e ON e.id = w.employee_id 
                WHERE e.name = ?
            """, (name,))

            works = []
            for work_type, hours in cursor.fetchall():
                works.append({WorkType[work_type]: hours})

            return works

    def get_all_employees(self) -> list[str]:
        """Получение списка всех сотрудников."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM employees")
            return [row[0] for row in cursor.fetchall()]

    def get_all_work_rates(self) -> dict[WorkType, float]:
        """Получение всех ставок за работу."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT work_type, rate FROM work_rates")
            return {WorkType[wt]: rate for wt, rate in cursor.fetchall()}

    def clear_employees_and_works(self) -> None:
        """Очистка только сотрудников и их работ из БД."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM works")
            cursor.execute("DELETE FROM employees")
            conn.commit()

    def clear_database(self) -> None:
        """Очистка всех таблиц в базе данных."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM works")
            cursor.execute("DELETE FROM work_rates")
            cursor.execute("DELETE FROM employees")
            conn.commit()

    def delete_employee(self, name: str) -> None:
        """Удаление сотрудника и всех его работ из БД."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id FROM employees WHERE name = ?", (name,))
                employee_id = cursor.fetchone()

                if employee_id:
                    employee_id = employee_id[0]
                    cursor.execute("DELETE FROM works WHERE employee_id = ?", (employee_id,))
                    cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))

                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                raise Exception(f"Ошибка при удалении сотрудника: {e}")
