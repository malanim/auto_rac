# menu_actions.py

import os
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

def get_cluster_credentials(encryption_handler, cluster_code):
    """Получить логин и пароль для кластера, если они уже сохранены."""
    try:
        cluster_user = encryption_handler.decrypt(f"cluster_user_{cluster_code}")
        cluster_pwd = encryption_handler.decrypt(f"cluster_pwd_{cluster_code}")
        return cluster_user, cluster_pwd
    except Exception:
        return '', ''

def set_cluster_credentials(encryption_handler, cluster_code, cluster_user, cluster_pwd):
    """Сохранить логин и пароль для кластера."""
    encryption_handler.encrypt(cluster_user, f"cluster_user_{cluster_code}")
    encryption_handler.encrypt(cluster_pwd, f"cluster_pwd_{cluster_code}")

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
            command_result = subprocess.CompletedProcess(args=e.cmd, returncode=e.returncode, stdout='', stderr=e.stderr)

    command_thread = threading.Thread(target=run_command)
    command_thread.start()

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
        return command_result.stdout

def process_cluster_info(cluster_info):
    """Обработать и вывести информацию о кластере."""
    try:
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

def connect_to_host(load_hosts, path_to_rac, encryption_handler):
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
                # Извлекаем cluster_code из cluster_info
                cluster_code = cluster_info.splitlines()[0].split(':')[1].strip()  # Предполагается, что код кластера находится в первой строке
                cluster_user, cluster_pwd = get_cluster_credentials(encryption_handler, cluster_code)  # Передаем cluster_code
                if not cluster_user or not cluster_pwd:
                    pass_handler = CredentialsManager()
                    cluster_user = input("Введите логин кластера: ")
                    cluster_pwd = pass_handler.get_password("Введите пароль кластера: ")
                    set_cluster_credentials(encryption_handler, cluster_code, cluster_user, cluster_pwd)  # Передаем cluster_code

                process_cluster_info(cluster_info)
                handle_cluster_actions(encryption_handler, cluster_info, selected_host, cluster_user, cluster_pwd)

def create_database(cluster, cluster_user, cluster_pwd, newdb, host_db_server, user, password, shedJobs, selected_host):
    """Создать новую базу данных в кластере."""
    command = f'{path_to_rac} infobase --cluster={cluster} create --create-database --cluster-user="{cluster_user}" --cluster-pwd="{cluster_pwd}" --name="{newdb}" --dbms=PostgreSQL --db-server={host_db_server} --db-name="{newdb}" --locale=ru --db-user="{user}" --db-pwd="{password}" --license-distribution=allow --scheduled-jobs-deny={shedJobs} {selected_host}'
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')
    
    if result.returncode == 0:
        print(f"База данных '{newdb}' успешно создана.")
        return result.stdout  # Возвращаем стандартный вывод
    else:
        print(f"Ошибка при создании базы данных:\n{result.stderr}")
        return result.stderr  # Возвращаем сообщение об ошибке

def delete_database(cluster, cluster_user, cluster_pwd, selected_host):
    """Удалить информационную базу по названию и разорвать подключения."""
    
    # Запрашиваем у пользователя название базы данных для удаления
    infobase_name = input("Введите название базы данных для удаления: ")
    
    # Запрашиваем у пользователя логин и пароль для PostgreSQL
    pass_handler = CredentialsManager()
    psql_user = input("Введите логин для PostgreSQL: ")
    psql_password = pass_handler.get_password("Введите пароль для PostgreSQL: ")
    
    # Разрываем подключения к базе данных
    os.environ['PGPASSWORD'] = psql_password
    command = [
        r"C:\Program Files\PostgreSQL\16.3-16.1C\bin\psql.exe",
        "-h", selected_host,
        "-U", psql_user,
        "-d", infobase_name,  # Используем infobase_name как имя базы данных
        "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{infobase_name}' AND pid <> pg_backend_pid();"
    ]

    try:
        # Выполнение команды
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        # print("Output:", result.stdout)

    except subprocess.CalledProcessError as e:
        print("Ошибка при разрыве подключений:", e)
        print("Output:", e.output)
        print("Error:", e.stderr.encode('cp1251').decode('utf-8'))

    finally:
        # Удаление переменной окружения
        del os.environ['PGPASSWORD']

    # Получаем список информационных баз
    command = f'{path_to_rac} infobase --cluster={cluster} --cluster-user={cluster_user} --cluster-pwd={cluster_pwd} summary list {selected_host}'
    # print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')

    if result.returncode != 0:
        print(f"Ошибка при получении списка информационных баз:\n{result.stderr}")
        return

    # Выводим список баз данных
    # print('Список информационных баз:\n')
    # print(result.stdout)

    # Находим id_infobase по названию infobase_name
    id_infobase = None
    lines = result.stdout.splitlines()
    for i in range(len(lines)):
        if 'name' in lines[i] and infobase_name in lines[i]:
            # Если нашли нужное имя, то берем id из предыдущей строки
            id_infobase = lines[i - 1].split(':')[1].strip()
            break

    if id_infobase is None:
        print(f"Информационная база с названием '{infobase_name}' не найдена.")
        return

    # Выполняем команду для удаления базы данных
    command = f'{path_to_rac} infobase --cluster={cluster} drop --drop-database --cluster-user="{cluster_user}" --cluster-pwd="{cluster_pwd}" --infobase={id_infobase} {selected_host}'
    print(command)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')

    if result.returncode == 0:
        print(f"Информационная база '{infobase_name}' успешно удалена.")
    else:
        print(f"Ошибка при удалении информационной базы:\n{result.stderr}")

def handle_cluster_actions(encryption_handler, cluster_info, selected_host, cluster_user, cluster_pwd):
    while True:
        options = ['Задать логин/пароль', 'Вывести список информационных баз', 'Создать новую базу данных', 'Удалить информационную базу', 'Назад']
        menu = InteractiveMenu(options, 'Выберите действие с кластером:')
        cluster_option_index = menu.display_menu()

        if cluster_option_index == 0:  # Задать логин/пароль
            pass_handler = CredentialsManager()
            cluster_user = input("Введите логин кластера: ")
            cluster_pwd = pass_handler.get_password("Введите пароль кластера: ")
            # Извлекаем cluster_code из cluster_info
            cluster_code = cluster_info.splitlines()[0].split(':')[1].strip()  # Предполагается, что код кластера находится в первой строке
            set_cluster_credentials(encryption_handler, cluster_code, cluster_user, cluster_pwd)
            print('Логин и пароль кластера сохранены.\n')
        elif cluster_option_index == 1:  # Вывести список информационных баз
            if 'cluster' in cluster_info:
                cluster_code = cluster_info.splitlines()[0].split(':')[1].strip()
                command = f'{path_to_rac} infobase --cluster={cluster_code} --cluster-user={cluster_user} --cluster-pwd={cluster_pwd} summary list {selected_host}'
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp866')

                if result.returncode != 0:
                    if "Ошибка операции администрирования" in result.stderr:
                        print("Ошибка: администратор кластера не аутентифицирован.")
                        pass_handler = CredentialsManager()
                        cluster_user = input("Введите логин кластера: ")
                        cluster_pwd = pass_handler.get_password("Введите пароль кластера: ")
                        set_cluster_credentials(encryption_handler, cluster_code, cluster_user, cluster_pwd)
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
                host_db_server = input("Введите адрес сервера базы данных: ")
                user = input("Введите имя пользователя базы данных: ")
                password = input("Введите пароль пользователя базы данных: ")
                shedJobs = "on"  # Параметры для запланированных задач
                creation_result = create_database(cluster_code, cluster_user, cluster_pwd, newdb, host_db_server, user, password, shedJobs, selected_host)
                print(f"Результат выполнения команды создания базы данных:\n{creation_result}")
            else:
                print("Не удалось получить код кластера.\n")
        elif cluster_option_index == 3:  # Удалить информационную базу
            if 'cluster' in cluster_info:
                cluster_code = cluster_info.splitlines()[0].split(':')[1].strip()
                delete_database(cluster_code, cluster_user, cluster_pwd, selected_host)
        elif cluster_option_index == 4:  # Назад
            break
