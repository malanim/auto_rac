import subprocess
from input_handler import InteractiveMenu, CredentialsManager  # Необходимые классы
from menu_actions import connect_to_host, load_hosts, path_to_rac  # Необходимые функции и переменные для работы с меню
import sys
from encryption_handler import EncryptionHandler  # Импортируем EncryptionHandler

hello_print = r'''
       __________________________________________________________________
  ____L\                         Добро пожаловать!                       \______
 /\       ______   __  __   ______  _____              ____     ______   ____   \
 \ \     /\  _  \ /\ \/\ \ /\__  _\/\  __`\           /\  _`\  /\  _  \ /\  _`\  \
  \ \    \ \ \L\ \\ \ \ \ \\/_/\ \/\ \ \/\ \          \ \ \L\ \\ \ \L\ \\ \ \/\_\ \
   \ \    \ \  __ \\ \ \ \ \  \ \ \ \ \ \ \ \   _______\ \ ,  / \ \  __ \\ \ \/_/_ \
    \ \    \ \ \/\ \\ \ \_\ \  \ \ \ \ \ \_\ \ /\______\\ \ \\ \ \ \ \/\ \\ \ \L\ \ \
     \ \    \ \_\ \_\\ \_____\  \ \_\ \ \_____\\/______/ \ \_\ \_\\ \_\ \_\\ \____/  \
      \ \    \/_/\/_/ \/_____/   \/_/  \/_____/           \/_/\/ / \/_/\/_/ \/___/    \
       \ \______                                                                  _____\
        \______/\_______Автоматическая_консоль_удаленного_администрирования_______\____/
               \/_________________________________________________________________/
'''

def exit_program():
    print("Выход из программы")
    sys.exit(0)

def authenticate_user(handler):
    pass_handler = CredentialsManager()
    login, password = pass_handler.get_credentials()
    if handler.authenticate_user(login, password):
        print(f"Пользователь '{login}' успешно аутентифицирован.")
        return True
    else:
        print("Неправильный логин или пароль.")
        return False

def register_user(handler):
    pass_handler = CredentialsManager()
    new_login, new_password = pass_handler.get_credentials()
    if handler.register_user(new_login, new_password):
        print(f"Пользователь '{new_login}' успешно зарегистрирован.")
    else:
        print(f"Пользователь с логином '{new_login}' уже существует.")

def main():
    print(hello_print)

    handler = EncryptionHandler("encrypted_data.json")  # Инициализация здесь

    while True:  # Бесконечный цикл
        options = ['Авторизация', 'Регистрация', 'Выход']
        menu = InteractiveMenu(options, 'Выберите действие:')
        selected_option_index = menu.display_menu()

        if selected_option_index == 0:  # Авторизация
            if authenticate_user(handler):  # Передаем handler
                break
        elif selected_option_index == 1:  # Регистрация
            register_user(handler)  # Передаем handler
        elif selected_option_index == 2:  # Выход
            exit_program()

    while True:  # Основное меню после успешной авторизации
        options = ['Подключиться', 'Настройки', 'Выход']
        menu = InteractiveMenu(options, 'Выберите действие:')
        selected_option_index = menu.display_menu()

        actions = {
            0: lambda: connect_to_host(load_hosts, path_to_rac, handler),  # Передаем handler
            1: lambda: print("Настройки еще не реализованы.\n"),
            2: exit_program,
        }

        # Вызываем соответствующую функцию по индексу
        if selected_option_index in actions:
            actions[selected_option_index]()
        else:
            print("Некорректный выбор. Пожалуйста, попробуйте снова.")

if __name__ == "__main__":
    main()