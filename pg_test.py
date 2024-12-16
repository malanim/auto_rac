import os
import subprocess

# Параметры подключения
host = '10.10.10.200'
user = 'postgres'
password = 'postgres'

# Установка переменной окружения для пароля
os.environ['PGPASSWORD'] = password

# Команда для подключения к psql и выполнения запроса
command = [
    r"C:\Program Files\PostgreSQL\16.3-16.1C\bin\psql.exe",
    "-h", host,
    "-U", user,
    "-c", '''SELECT datname AS "Name", 
                pg_size_pretty(pg_database_size(datname)) AS "Size"
            FROM pg_database
            ORDER BY pg_database_size(datname) DESC;
            '''
]

try:
    # Выполнение команды
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    print("Output:\n" + result.stdout)

except subprocess.CalledProcessError as e:
    print("An error occurred:\n", e)
    print("Output:\n", e.output)
    # print("Error:", result.stderr)
    print("Error:\n", e.stderr.encode('cp1251').decode('utf-8'))

finally:
    # Удаление переменной окружения
    del os.environ['PGPASSWORD']
