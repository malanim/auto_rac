import subprocess

# Параметры подключения к базе данных
db_config = {
    'dbname': 'test1',
    'user': 'postgres',
    'password': 'postgres',
    'host': '10.10.10.200'
}

def reset_connections(db_config):
    # Формируем команду для выполнения
    command = [
        r'"C:\Program Files\PostgreSQL\16.3-16.1C\bin\psql.exe"',
        '-h', db_config['host'],
        '-U', db_config['user'],
        '-d', db_config['dbname'],
        '-c', """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{dbname}' AND pid <> pg_backend_pid();
        """.format(dbname=db_config['dbname'])
    ]

    # Устанавливаем переменную окружения для пароля
    env = {'PGPASSWORD': db_config['password']}

    # Выводим полную команду
    print("Выполняем команду:")
    print(" ".join(command))
    
    try:
        # Выполняем команду
        subprocess.run(command, env=env, check=True)
        print(f"Все подключения к базе данных '{db_config['dbname']}' сброшены.")
    except subprocess.CalledProcessError as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    reset_connections(db_config)