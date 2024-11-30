from typing import Callable
import tkinter as tk
from tkinter import ttk, messagebox

from models.work_type import WorkType
from models.payroll import PayrollDepartment


class RateWindow:
    """Окно управления ставками для различных типов работ."""

    def __init__(self, parent: tk.Tk, payroll: PayrollDepartment, callback: Callable | None = None) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Управление ставками")
        self.window.geometry("400x500")

        self.payroll = payroll
        self.callback = callback

        self._create_widgets()
        self._load_rates()

    def _create_widgets(self) -> None:
        """Создание и размещение всех виджетов окна."""
        self._create_treeview()
        self._create_form()

    def _create_treeview(self) -> None:
        """Создание таблицы ставок."""
        self.tree = ttk.Treeview(self.window, columns=("Тип", "Ставка"), show="headings")

        self.tree.heading("Тип", text="Тип работы")
        self.tree.heading("Ставка", text="Ставка за час")
        self.tree.column("Тип", width=200, anchor="center")
        self.tree.column("Ставка", width=100, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<Double-1>", self._on_double_click)

    def _create_form(self) -> None:
        """Создание формы добавления/изменения ставки."""
        form_frame = self._create_form_frame()
        self._create_work_type_section(form_frame)
        self._create_rate_section(form_frame)
        self._create_button_section(form_frame)

    def _create_form_frame(self) -> ttk.LabelFrame:
        """Создание рамки формы."""
        form_frame = ttk.LabelFrame(self.window, text="Добавление/изменение ставки")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        return form_frame

    def _create_work_type_section(self, parent: ttk.LabelFrame) -> None:
        """Создание секции выбора типа работы."""
        ttk.Label(parent, text="Тип работы:").pack(anchor=tk.W, padx=5, pady=2)

        self.work_type_var = tk.StringVar()
        self.work_type_combo = ttk.Combobox(
            parent,
            textvariable=self.work_type_var,
            values=[wt.name for wt in WorkType],
        )
        self.work_type_combo.pack(fill=tk.X, padx=5, pady=2)

    def _create_rate_section(self, parent: ttk.LabelFrame) -> None:
        """Создание секции ввода ставки."""
        ttk.Label(parent, text="Ставка за час:").pack(anchor=tk.W, padx=5, pady=2)
        self.rate_entry = ttk.Entry(parent)
        self.rate_entry.pack(fill=tk.X, padx=5, pady=2)

    def _create_button_section(self, parent: ttk.LabelFrame) -> None:
        """Создание секции с кнопками."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(button_frame, text="Сохранить", command=self.add_rate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self._clear_form).pack(side=tk.LEFT, padx=5)

    def _on_double_click(self, event: tk.Event) -> None:
        """Обработчик двойного клика по ставке."""
        item = self.tree.identify_row(event.y)
        if not item:
            return

        work_type_name, current_rate = self.tree.item(item)["values"]

        self.work_type_var.set(work_type_name)
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, current_rate)

    def _load_rates(self) -> None:
        """Загрузка существующих ставок в таблицу"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for work_type, rate in self.payroll.work_rates.items():
            self.tree.insert("", tk.END, values=(work_type.name, f"{rate:.2f}"))

    def add_rate(self) -> None:
        """Добавление или обновление ставки"""
        try:
            work_type_name = self.work_type_var.get()
            if not work_type_name:
                raise ValueError("Выберите тип работы")

            rate = self.rate_entry.get()
            if not rate:
                raise ValueError("Введите ставку")

            self.payroll.add_work_rate(WorkType[work_type_name], float(rate))

            self._load_rates()
            self._clear_form()

            if self.callback:
                self.callback()

            messagebox.showinfo("Успех", f"Ставка для {work_type_name} установлена: {float(rate):.2f}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def _clear_form(self) -> None:
        """Очистка формы заполнения ставки."""
        self.work_type_var.set("")
        self.rate_entry.delete(0, tk.END)
