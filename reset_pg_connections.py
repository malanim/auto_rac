import os
import subprocess

# Параметры подключения
host = 'host'
dbname = 'test1'
user = 'postgres'
password = 'pwd'

# Установка переменной окружения для пароля
os.environ['PGPASSWORD'] = password

# Команда для подключения к psql и выполнения запроса
command = [
    r"C:\Program Files\PostgreSQL\16.3-16.1C\bin\psql.exe",
    "-h", host,
    "-U", user,
    "-d", dbname,
    "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{dbname}' AND pid <> pg_backend_pid();"
]

try:
    # Выполнение команды
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    print("Output:", result.stdout)

except subprocess.CalledProcessError as e:
    print("An error occurred:", e)
    print("Output:", e.output)
    # print("Error:", result.stderr)
    print("Error:", e.stderr.encode('cp1251').decode('utf-8'))

finally:
    # Удаление переменной окружения
    del os.environ['PGPASSWORD']
