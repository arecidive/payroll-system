from app.main_window import MainWindow


def main() -> None:
    """Запуск оконного приложения."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
