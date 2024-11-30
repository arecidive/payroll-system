from typing import Optional, Any
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from app.employee_window import EmployeeWindow
from app.rate_window import RateWindow
from app.work_window import WorkWindow
from models.work_type import WorkType
from models.payroll import PayrollDepartment


class MainWindow:
    """Главное окно приложения для управления системой расчета зарплат."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Система расчета зарплат")
        self.root.geometry("1115x600")

        self.payroll = PayrollDepartment()
        self.tree = None
        self.context_menu = None
        self.sort_column = "Имя"
        self.sort_reverse = False

        self._create_widgets()

    def run(self) -> None:
        """Запуск главного цикла приложения."""
        self.root.mainloop()

    def _create_widgets(self) -> None:
        """Создание и размещение всех виджетов главного окна."""
        self._create_button_frame()
        self._create_treeview()
        self.root.bind("<Delete>", lambda event: self._delete_employee())

    def _create_button_frame(self) -> None:
        """Создание фрейма с кнопками управления."""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        buttons = [
            ("Добавить сотрудника", self._open_add_employee),
            ("Добавить работу", self._open_add_work),
            ("Очистить всех сотрудников", self._clear_all_employees),
            ("Управление ставками", self._open_rates),
            ("Загрузить из файла", self._load_from_file),
            ("Сохранить в файл", self._save_to_file),
        ]

        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

    def _create_treeview(self) -> None:
        """Создание таблицы для отображения сотрудников."""
        self.tree = ttk.Treeview(self.root, columns=("Имя", "Зарплата"), show="headings")

        self.tree.heading("Имя", text="Имя ↕", command=lambda: self._sort_column("Имя"))
        self.tree.heading("Зарплата", text="Зарплата ↕", command=lambda: self._sort_column("Зарплата"))

        self.tree.column("Имя", width=200, anchor="center")
        self.tree.column("Зарплата", width=100, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.sort_column = "Имя"
        self.sort_reverse = False

    def _sort_column(self, column: str) -> None:
        """Сортировка данных в таблице по указанному столбцу."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        items = [(self.tree.set(item, column), item) for item in self.tree.get_children("")]
        if column == "Зарплата":
            items.sort(key=lambda x: float(x[0]), reverse=self.sort_reverse)
        else:
            items.sort(key=lambda x: x[0].lower(), reverse=self.sort_reverse)

        for index, (_, item) in enumerate(items):
            self.tree.move(item, "", index)

        self._update_headers()

    def _update_headers(self) -> None:
        """Обновление заголовков таблицы с индикаторами сортировки."""
        for col in ("Имя", "Зарплата"):
            text = col
            if col == self.sort_column:
                text += " ↑" if not self.sort_reverse else " ↓"
            else:
                text += " ↕"
            self.tree.heading(col, text=text, command=lambda c=col: self._sort_column(c))

    def _update_table(self) -> None:
        """Обновление таблицы сотрудников с сохранением текущей сортировки."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for name, employee in self.payroll.employees.items():
            total_salary = employee.calculate_salary(self.payroll.work_rates)
            self.tree.insert("", tk.END, values=(name, f"{total_salary:.2f}"))

        if hasattr(self, "sort_column"):
            self._sort_column(self.sort_column)
            self._sort_column(self.sort_column)

    def _open_rates(self) -> None:
        """Открытие окна управления ставками."""
        RateWindow(self.root, self.payroll, callback=self._update_table)

    def _open_add_employee(self) -> None:
        """Открытие окна добавления нового сотрудника."""
        EmployeeWindow(self.root, self.payroll, callback=self._update_table)

    def _open_add_work(self) -> None:
        """Открытие окна добавления работы."""
        if not self.payroll.employees:
            messagebox.showwarning("Предупреждение", "Сначала добавьте сотрудника")
            return
        WorkWindow(self.root, self.payroll, callback=self._update_table)

    def _clear_all_employees(self) -> None:
        """Удаление всех сотрудников из системы с подтверждением."""
        try:
            if not self.payroll.employees:
                messagebox.showinfo("Информация", "Список сотрудников пуст")
                return

            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить всех сотрудников?"):
                self.payroll.employees.clear()
                self._update_table()
                messagebox.showinfo("Успех", "Все сотрудники удалены")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def _delete_employee(self) -> None:
        """Удаление выбранного сотрудника с подтверждением."""
        try:
            selected = self.tree.selection()
            if not selected:
                messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
                return

            employee_name = self.tree.item(selected[0])["values"][0]
            if messagebox.askyesno("Подтверждение", f"Удалить сотрудника '{employee_name}'?"):
                self.payroll.delete_employee(str(employee_name))
                self._update_table()
                messagebox.showinfo("Успех", f"Сотрудник '{employee_name}' удален")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def _save_to_file(self) -> None:
        """Сохранение данных о сотрудниках и ставках в JSON файл."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            data = self._prepare_data_for_save()
            self._write_data_to_file(filename, data)
            messagebox.showinfo("Успех", "Данные успешно сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def _prepare_data_for_save(self) -> dict[str, Any]:
        """Подготовка данных для сохранения в файл."""
        return {
            "employees": {
                name: {
                    "works": [
                        {work_type.name: hours for work_type, hours in work.items()}
                        for work in employee.works
                    ],
                }
                for name, employee in self.payroll.employees.items()
            },
            "work_rates": {wt.name: rate for wt, rate in self.payroll.work_rates.items()},
        }

    def _write_data_to_file(self, filename: str, data: dict[str, Any]) -> None:
        """Запись данных в файл."""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def _load_from_file(self) -> None:
        """Загрузка данных о сотрудниках и ставках из JSON файла."""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])

        if not filename:
            return

        try:
            self._load_data_from_file(filename)
            self._update_table()
            messagebox.showinfo("Успех", "Данные успешно загружены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _load_data_from_file(self, filename: str) -> None:
        """Загрузка и обработка данных из файла."""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.payroll.employees.clear()
        self.payroll.work_rates.clear()

        # Загрузка ставок
        for work_type_name, rate in data["work_rates"].items():
            self.payroll.add_work_rate(WorkType[work_type_name], rate)

        # Загрузка сотрудников и их работ
        for name, employee_data in data["employees"].items():
            self.payroll.add_employee(name)
            for work in employee_data["works"]:
                for work_type_name, hours in work.items():
                    self.payroll.add_work(name, WorkType[work_type_name], hours)
