from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox

from models.work_type import WorkType
from models.payroll import PayrollDepartment


class WorkWindow:
    """Окно добавления работы для сотрудника."""

    def __init__(self, parent: tk.Tk, payroll: PayrollDepartment, callback: Callable | None = None) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление работы")
        self.window.geometry("400x500")

        self.payroll = payroll
        self.callback = callback

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Создание и размещение всех виджетов окна."""
        self._create_employee_section()
        self._create_work_section()
        self._create_button_section()

    def _create_employee_section(self) -> None:
        """Создание секции выбора сотрудника."""
        frame = self._create_labeled_frame("Выбор сотрудника")
        self._create_employee_field(frame)

    def _create_employee_field(self, parent: ttk.LabelFrame) -> None:
        """Создание поля выбора сотрудника."""
        ttk.Label(parent, text="Сотрудник:").pack(anchor=tk.W, padx=5, pady=2)

        self.employee_var = tk.StringVar()
        self.employee_combo = ttk.Combobox(
            parent,
            textvariable=self.employee_var,
            values=list(self.payroll.employees.keys())
        )
        self.employee_combo.pack(fill=tk.X, padx=5, pady=2)

    def _create_work_section(self) -> None:
        """Создание секции данных работы."""
        frame = self._create_labeled_frame("Данные работы")
        self._create_work_type_field(frame)
        self._create_hours_field(frame)

    def _create_work_type_field(self, parent: ttk.LabelFrame) -> None:
        """Создание поля выбора типа работы."""
        ttk.Label(parent, text="Тип работы:").pack(anchor=tk.W, padx=5, pady=2)

        self.work_type_var = tk.StringVar()
        self.work_type_combo = ttk.Combobox(
            parent,
            textvariable=self.work_type_var,
            values=[wt.name for wt in WorkType]
        )
        self.work_type_combo.pack(fill=tk.X, padx=5, pady=2)

    def _create_hours_field(self, parent: ttk.LabelFrame) -> None:
        """Создание поля ввода количества часов."""
        ttk.Label(parent, text="Количество часов:").pack(anchor=tk.W, padx=5, pady=2)
        self.hours_entry = ttk.Entry(parent)
        self.hours_entry.pack(fill=tk.X, padx=5, pady=2)

    def _create_button_section(self) -> None:
        """Создание секции с кнопками."""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Добавить", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def _create_labeled_frame(self, text: str) -> ttk.LabelFrame:
        """Создание рамки с заголовком."""
        frame = ttk.LabelFrame(self.window, text=text)
        frame.pack(fill=tk.X, padx=5, pady=5)
        return frame

    def _save(self) -> None:
        """Добавление работы сотруднику."""
        try:
            employee_name = self.employee_var.get()
            if not employee_name:
                raise ValueError("Выберите сотрудника")

            work_type_name = self.work_type_var.get()
            if not work_type_name:
                raise ValueError("Выберите тип работы")

            hours = self.hours_entry.get()
            if not hours:
                raise ValueError("Введите количество часов")

            self.payroll.add_work(employee_name, WorkType[work_type_name], float(hours))

            if self.callback:
                self.callback()

            messagebox.showinfo("Успех", f"Работа успешно добавлена сотруднику '{employee_name}'")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
