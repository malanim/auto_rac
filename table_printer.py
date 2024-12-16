class TablePrinter:
    def __init__(self, column_names):
        self.column_names = ["№"] + column_names  # Добавление заголовка "№"
        self.num_columns = len(self.column_names)

    def print_table(self, data):
        # Печать заголовков
        header = " | ".join(self.column_names)
        print(header)
        print("-" * len(header))  # Граница между заголовками и данными

        # Определение максимальной ширины для каждого столбца, включая заголовки
        max_widths = [max(len(str(item)) for item in col) for col in zip(*data, self.column_names)]
        
        # Печать данных с нумерацией строк
        for index, row in enumerate(data, start=1):
            row_data = " | ".join(f"{str(item):<{max_widths[i]}}" for i, item in enumerate(row))
            print(f"{index:<3} | {row_data}")

if __name__ == "__main__":
    # Пример имен столбцов
    column_names = ["Имя", "Возраст", "Город"]
    
    # Пример данных
    data = [
        ["Алексей", 30, "Москва"],
        ["Мария", 25, "Санкт-Петербург"],
        ["Иван", 22, "Казань"]
    ]
    
    # Создание экземпляра класса
    table_printer = TablePrinter(column_names)
    
    # Печать таблицы
    table_printer.print_table(data)