from encryption_handler import EncryptionHandler
from input_handler import CredentialsManager, InteractiveMenu

def main():
    json_file = "encrypted_data.json"
    handler = EncryptionHandler(json_file)
    
    while True:
        try:
            # First layer menu
            first_layer_options = [
                'Авторизация',
                'Регистрация',
                'Выход'
            ]
            first_layer_menu = InteractiveMenu(first_layer_options, "Выберите действие:")
            first_layer_selected_option_index = first_layer_menu.display_menu()

            if first_layer_selected_option_index == 0:
                # Authentication
                pass_handler = CredentialsManager()
                login, password = pass_handler.get_credentials()
                print(f'l: {login}\np: {password}')
                if handler.authenticate_user(login, password):
                    print(f"Пользователь '{login}' успешно аутентифицирован.")
                    # Second layer menu
                    while True:
                        second_layer_options = [
                            'Расшифровать всё',
                            'Расшифровать определенную строку',
                            'Добавить новую строку (по названию)',
                            'Удалить строку (по названию)',
                            'Изменить строку (по названию)',
                            'Выйти на предыдущий слой',
                            'Выход из программы'
                        ]
                        second_layer_menu = InteractiveMenu(second_layer_options, "Выберите действие:")
                        second_layer_selected_option_index = second_layer_menu.display_menu()

                        if second_layer_selected_option_index == 0:
                            all_data = handler.get_all_encrypted_data()
                            for name, encrypted_data in all_data.items():
                                try:
                                    decrypted_data = handler.decrypt(name)
                                    print(f"Name: {name}, Decrypted data: {decrypted_data}")
                                except Exception as e:
                                    print(f"Ошибка при расшифровке строки '{name}': {e}")
                        elif second_layer_selected_option_index == 1:
                            name = input("Введите название строки для расшифровки: ")
                            try:
                                decrypted_data = handler.decrypt(name)
                                print(f"Decrypted data: {decrypted_data}")
                            except Exception as e:
                                print(f"Ошибка при расшифровке строки '{name}': {e}")
                        elif second_layer_selected_option_index == 2:
                            data_to_encrypt = input("Введите строку для шифрования: ")
                            name = input("Введите название строки: ")
                            encrypted_data = handler.encrypt(data_to_encrypt, name)
                            print(f"Encrypted data: {encrypted_data}")
                        elif second_layer_selected_option_index == 3:
                            name = input("Введите название строки для удаления: ")
                            if handler.delete_data(name):
                                print(f"Строка '{name}' удалена.")
                            else:
                                print(f"Строка '{name}' не найдена.")
                        elif second_layer_selected_option_index == 4:
                            name = input("Введите название строки для изменения: ")
                            if handler.update_data(name, input("Введите новую строку: ")):
                                print(f"Строка '{name}' изменена.")
                            else:
                                print(f"Строка '{name}' не найдена.")
                        elif second_layer_selected_option_index == 5:
                            break  # Exit to the first layer menu
                        elif second_layer_selected_option_index == 6:
                            return  # Exit the program
                else:
                    print("Неправильный логин или пароль.")
            elif first_layer_selected_option_index == 1:
                # Registration
                pass_handler = CredentialsManager()
                new_login, new_password = pass_handler.get_credentials()
                if handler.register_user(new_login, new_password):
                    print(f"Пользователь '{new_login}' успешно зарегистрирован.")
                else:
                    print(f"Пользователь с логином '{new_login}' уже существует.")
            elif first_layer_selected_option_index == 2:
                break  # Exit the program
        
        except Exception as e:
            print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
