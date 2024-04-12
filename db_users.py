
import sqlite3

# Создаем подключение к базе данных пользователей
conn_users = sqlite3.connect('users.db')
cursor_users = conn_users.cursor()

# Создаем таблицу 'users', если ее еще нет
cursor_users.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        patronymic TEXT
    )
''')

# Закрываем соединение с базой данных пользователей
cursor_users.close()
conn_users.close()
