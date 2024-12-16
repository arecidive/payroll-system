from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox

from models.payroll import PayrollDepartment


class EmployeeWindow:
    """Окно для добавления нового сотрудника."""

    def __init__(self, parent: tk.Tk, payroll: PayrollDepartment, callback: Callable | None = None) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Добавление сотрудника")
        self.window.geometry("400x200")

        self.payroll = payroll
        self.callback = callback

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Создание и размещение всех виджетов окна с добавлением сотрудников."""
        frame = ttk.LabelFrame(self.window, text="Данные сотрудника")
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(frame, text="Имя:").pack(anchor=tk.W, padx=5, pady=2)

        self.name_entry = ttk.Entry(frame)
        self.name_entry.pack(fill=tk.X, padx=5, pady=2)

        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Сохранить", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

    def _save(self) -> None:
        """Сохранение нового сотрудника."""
        try:
            name = str(self.name_entry.get().strip())

            self.payroll.add_employee(name)
            if self.callback:
                self.callback()

            messagebox.showinfo("Успех", f"Сотрудник '{name}' успешно добавлен")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
