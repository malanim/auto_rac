# menu_actions.py

import subprocess
from input_handler import CredentialsManager, InteractiveMenu  # Импортируйте необходимые классы
import threading
import time
from pathlib import Path

# Путь до утилиты
path_to_rac = r'"C:\Program Files\1cv8\8.3.24.1761\bin\rac.exe"'
hosts_file_path = Path('c:/git_proj/auto_rac/hosts.txt')
command_result = None
stop_event = threading.Event()

def load_hosts():
    """Загрузить хосты из файла."""
    if hosts_file_path.exists():
        with hosts_file_path.open('r') as file:
            return [line.strip() for line in file if line.strip()]
    return []

def save_hosts(hosts):
    """Сохранить хосты в файл."""
    with hosts_file_path.open('w') as file:
        for host in hosts:
            file.write(f"{host}\n")

def add_host(hosts):
    """Добавить новый хост."""
    new_host = input("Введите новый хост: ")
    hosts.append(new_host)
    save_hosts(hosts)

def delete_host(hosts):
    """Удалить существующий хост с подтверждением."""
    menu = InteractiveMenu(hosts, 'Выберите хост для удаления:')
    selected_option_index = menu.display_menu()

    if selected_option_index is not None:
        selected_host = hosts[selected_option_index]
        confirmation_menu = InteractiveMenu(['Нет', 'Да'], f"Вы уверены, что хотите удалить хост '{selected_host}'?")
        confirmation_index = confirmation_menu.display_menu()

        if confirmation_index == 1:  # Если выбрали "Да"
            hosts.pop(selected_option_index)  # Удаляем хост
            save_hosts(hosts)
            print(f"Хост '{selected_host}' был успешно удален.")
        else:
            print("Удаление отменено.")

def execute_command(host):
    """Выполнить команду на выбранном хосте и вернуть результат."""
    global command_result
    command = f'{path_to_rac} cluster list {host}'

    print(f'Подключение к хосту "{host}"...\n')
    
    def run_command():
        global command_result
        try:
            command_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        except subprocess.CalledProcessError as e:
            # Создаем объект с атрибутами stdout и stderr
            command_result = subprocess.CompletedProcess(args=e.cmd, returncode=e.returncode, stdout='', stderr=e.stderr)

    # Запуск команды в отдельном потоке
    command_thread = threading.Thread(target=run_command)
    command_thread.start()

    # Ожидание завершения команды с тайм-аутом
    timeout = 10  # Время ожидания в секундах
    for _ in range(timeout):
        if command_thread.is_alive():
            time.sleep(1)
        else:
            break

    if command_thread.is_alive():
        stop_event.set()  # Устанавливаем флаг остановки
        command_thread.join()  # Ждем завершения потока
        print("Время ожидания истекло. Команда была отменена.")
        return None
    else:
        # Подключение успешно
        return command_result.stdout

def process_cluster_info(cluster_info):
    """Обработать и вывести информацию о кластере."""
    try:
        # Декодируем информацию о кластере с помощью кодировки CP866
        cluster_info = cluster_info.encode('cp1251').decode('cp866')
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        print(f"Ошибка декодирования: {e}")
        return

    lines = cluster_info.strip().split('\n')
    cluster_data = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            cluster_data[key.strip()] = value.strip()

    print("Информация о кластере:")
    for key, value in cluster_data.items():
        print(f"{key}: {value}")
    print('')

def connect_to_host(load_hosts, path_to_rac):
    hosts = load_hosts()
    if not hosts:
        print("Список хостов пуст. Пожалуйста, добавьте хост.")
        add_host(hosts)

    while True:  # Цикл для меню подключения
        options = hosts + ['Добавить новый', 'Удалить существующее', 'Назад']
        menu = InteractiveMenu(options, 'Выберите хост:')
        selected_option_index = menu.display_menu()

        if selected_option_index == len(hosts):  # Если выбрали "Добавить новый"
            add_host(hosts)
        elif selected_option_index == len(hosts) + 1:  # Если выбрали "Удалить существующее"
            delete_host(hosts)
        elif selected_option_index == len(hosts) + 2:  # Если выбрали "Назад"
            break
        else:
            selected_host = hosts[selected_option_index]
            cluster_info = execute_command(selected_host)
            if cluster_info:
                process_cluster_info(cluster_info)
                handle_cluster_actions(cluster_info, selected_host)

def create_database(cluster, cluster_user, cluster_pwd, newdb, host_db_server, user, password, shedJobs, selected_host):
    """Создать новую базу данных в кластере."""
    command = f'{path_to_rac} infobase --cluster={cluster} create --create-database --cluster-user="{cluster_user}" --cluster-pwd="{cluster_pwd}" --name="{newdb}" --dbms=PostgreSQL --db-server={host_db_server} --db-name="{newdb}" --locale=ru --db-user="{user}" --db-pwd="{password}" --license-distribution=allow --scheduled-jobs-deny={shedJobs} {selected_host}'
    # print(f'\n{command}\n')
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')
    
    if result.returncode == 0:
        print(f"База данных '{newdb}' успешно создана.")
        return result.stdout  # Возвращаем стандартный вывод
    else:
        print(f"Ошибка при создании базы данных:\n{result.stderr}")
        return result.stderr  # Возвращаем сообщение об ошибке

def handle_cluster_actions(cluster_info, selected_host):
    cluster_user, cluster_pwd = '', ''
    while True:
        options = ['Задать логин/пароль', 'Вывести список информационных баз', 'Создать новую базу данных', 'Назад']
        menu = InteractiveMenu(options, 'Выберите действие с кластером:')
        cluster_option_index = menu.display_menu()

        if cluster_option_index == 0:  # Задать логин/пароль
            manager = CredentialsManager()
            cluster_user, cluster_pwd = manager.get_credentials()
            print('')
        elif cluster_option_index == 1:  # Вывести список информационных баз
            if 'cluster' in cluster_info:
                cluster_code = cluster_info.splitlines()[0].split(':')[1].strip()
                command = f'{path_to_rac} infobase --cluster={cluster_code} --cluster-user={cluster_user} --cluster-pwd={cluster_pwd} summary list {selected_host}'
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')

                if result.returncode != 0:
                    if "Ошибка операции администрирования" in result.stderr:
                        print("Ошибка: администратор кластера не аутентифицирован.")
                        manager = CredentialsManager()
                        cluster_user, cluster_pwd = manager.get_credentials()
                        print('')
                        # Повторный запрос с новыми данными
                        command = f'{path_to_rac} infobase --cluster={cluster_code} --cluster-user={cluster_user} --cluster-pwd={cluster_pwd} summary list {selected_host}'
                        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')
                
                print('Список информационных баз:\n')
                print(result.stdout if result.returncode == 0 else result.stderr)
            else:
                print("Не удалось получить код кластера.\n")
        elif cluster_option_index == 2:  # Создать новую базу данных
            if 'cluster' in cluster_info:
                cluster_code = cluster_info.splitlines()[0].split(':')[1].strip()
                newdb = input("Введите имя новой базы данных: ")
                host_db_server = input("Введите адрес сервера базы данных: ")  # Новый ввод
                user = input("Введите имя пользователя базы данных: ")
                password = input("Введите пароль пользователя базы данных: ")
                shedJobs = "on"  # Параметры для запланированных задач
                creation_result = create_database(cluster_code, cluster_user, cluster_pwd, newdb, host_db_server, user, password, shedJobs, selected_host)
                print(f"Результат выполнения команды создания базы данных:\n{creation_result}")  # Выводим результат
            else:
                print("Не удалось получить код кластера.\n")
        elif cluster_option_index == 3:  # Назад
            break