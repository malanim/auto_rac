import os
import sys
import getpass
import platform

# Импортируем модули для работы с терминалом
if platform.system() == 'Windows':
    import msvcrt
else:
    import curses
    import tty
    import termios

class InteractiveMenu:
    """
    Класс для создания интерактивного текстового меню.

    Атрибуты:
        options (list): Список вариантов для отображения в меню.
        prompt (str): Текст, который будет отображаться перед выбором варианта.
        clear_screen_option (bool): Опция для очистки экрана.
    """
    
    def __init__(self, options, prompt="Выберите вариант:", clear_screen=True):
        """
        Инициализация класса InteractiveMenu.

        Параметры:
            options (list): Список вариантов для отображения в меню.
            prompt (str): Текст, который будет отображаться перед выбором варианта.
            clear_screen (bool): Опция для очистки экрана. По умолчанию True.
        """
        self.options = options
        self.current_row = 0
        self.clear_screen_option = clear_screen
        self.prompt = prompt

    def display_menu(self):
        """Отображение меню и обработка ввода пользователя."""
        if os.name == 'nt':  # Если операционная система Windows
            return self._display_menu_windows()
        else:  # Если операционная система Linux
            return self._display_menu_linux()

    def _display_menu_windows(self):
        """Отображение меню для Windows."""
        import os

        while True:
            print(self.prompt)  # Выводим текст перед выбором
            for i, option in enumerate(self.options):
                if i == self.current_row:
                    print(f"> {option}")  # Подсветка выбранного варианта
                else:
                    print(f"  {option}")

            key = msvcrt.getch()  # Чтение нажатой клавиши

            # Перемещение по меню
            if key == b'w' and self.current_row > 0:
                self.current_row -= 1
            elif key == b's' and self.current_row < len(self.options) - 1:
                self.current_row += 1
            elif key in [b'\x00', b'\xe0']:
                key = msvcrt.getch()
                if key == b'H' and self.current_row > 0:
                    self.current_row -= 1
                elif key == b'P' and self.current_row < len(self.options) - 1:
                    self.current_row += 1
            elif key in [b'\r', b'\n']:
                # Очистка заголовка и меню
                print("\033[F" * (len(self.options) + 1), end='')  # Возврат курсора на начало области с выбором
                print(" " * len(self.prompt))  # Стираем заголовок
                for _ in self.options:
                    print(" " * 50)  # Стираем строки меню пробелами
                print("\033[F" * (len(self.options) + 1), end='')  # Возврат курсора на начало области с выбором
                return self.current_row

            # Очистка только области с выбором
            print("\033[F" * (len(self.options) + 1), end='')  # Возврат курсора на начало области с выбором

    def _display_menu_linux(self):
        """Отображение меню для Linux."""

        def curses_main(stdscr):
            current_row = 0
            stdscr.clear()  # Очищаем экран в начале

            while True:
                stdscr.addstr(0, 0, self.prompt)  # Выводим текст перед выбором
                for idx, option in enumerate(self.options):
                    if idx == current_row:
                        stdscr.addstr(idx + 1, 0, option, curses.A_REVERSE)  # Подсветка выбранного варианта
                    else:
                        stdscr.addstr(idx + 1, 0, option)

                stdscr.refresh()  # Обновляем экран
                key = stdscr.getch()  # Чтение нажатой клавиши

                # Перемещение по меню
                if key == curses.KEY_UP and current_row > 0:
                    current_row -= 1
                elif key == curses.KEY_DOWN and current_row < len(self.options) - 1:
                    current_row += 1
                elif key in [10, 13]:  # Enter key
                    # Очистка заголовка и меню
                    stdscr.move(0, 0)  # Перемещение курсора на начало
                    stdscr.clrtoeol()  # Стираем заголовок
                    for idx in range(len(self.options)):
                        stdscr.addstr(idx + 1, 0, " " * len(self.options[idx]))  # Стираем строки меню пробелами
                    stdscr.refresh()
                    return current_row

                # Обновление только области с выбором
                stdscr.move(1, 0)  # Перемещение курсора на начало области с выбором
                for idx in range(len(self.options)):
                    stdscr.clrtoeol()  # Очистка строки до конца

        return curses.wrapper(curses_main)  # Запускаем основную функцию curses

# Пример использования класса InteractiveMenu
# if __name__ == "__main__":
#     options = ["Вариант 1", "Вариант 2", "Вариант 3", "Выйти"]
#     menu = InteractiveMenu(options, "Вариант:")
#     selected_option_index = menu.display_menu()  # Отображаем меню и получаем выбранный вариант
#     print(f"Вы выбрали вариант номер: {selected_option_index + 1}")  # +1 для отображения номера в 1-индексации

class CredentialsManager:
    def __init__(self):
        self.os_type = platform.system()

    def get_credentials(self):
        """Запросить логин и пароль для кластера."""
        user = input("Введите логин для кластера: ")
        pwd = self.get_password()  # Используем метод для получения пароля
        return user, pwd

    def get_password(self, prompt="Введите пароль для кластера: "):
        """Получить пароль, отображая символы в виде звездочек."""
        if self.os_type == 'Windows':
            return self._get_password_windows(prompt)
        else:
            return self._get_password_unix(prompt)

    def _get_password_windows(self, prompt):
        """Запросить пароль для Windows."""
        print(prompt, end='', flush=True)
        password = ''
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):
                print()  # Перевод строки
                break
            elif ch == b'\x08':  # Backspace
                if password:
                    password = password[:-1]
                    sys.stdout.write('\b \b')  # Удаляем последний символ
                    sys.stdout.flush()  # Обновляем вывод
            else:
                password += ch.decode('utf-8')
                sys.stdout.write('*')  # Показываем звездочку
                sys.stdout.flush()  # Обновляем вывод
        return password

    def _get_password_unix(self, prompt):
        """Запросить пароль для UNIX-подобных систем."""
        print(prompt, end='', flush=True)
        password = ''
        while True:
            ch = self.getch()
            if ch in ('\n', '\r', '\r\n'):
                print()  # Перевод строки
                break
            elif ch == '\x7f':  # Backspace
                if password:
                    password = password[:-1]
                    sys.stdout.write('\b \b')  # Удаляем последний символ
                    sys.stdout.flush()  # Обновляем вывод
            else:
                password += ch
                sys.stdout.write('*')  # Показываем звездочку
                sys.stdout.flush()  # Обновляем вывод
        return password

    def getch(self):
        """Читать один символ с клавиатуры (для UNIX)."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

# Пример использования класса CredentialsManager
if __name__ == "__main__":
    manager = CredentialsManager()
    user, pwd = manager.get_credentials()
    print(f"Логин: {user}, Пароль: {pwd}")  # Для проверки