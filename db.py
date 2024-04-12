import sqlite3

# Создаем подключение к базе данных
conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Создаем таблицу 'products', если ее еще нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL,
        photo TEXT,
        quantity INTEGER 
    )
''')

# Добавляем товары в таблицу
products = [
    (1, 'Пикник', 'Вкусные закуски для пикника.', 6400, 'https://kalachpek.ru/wp-content/uploads/2020/04/55.jpg', 20),
    (2, 'Беляш', 'Сочные беляши.', 50000, 'https://api.zlatapechka.ru/media/cache/7b/fb/7bfbd2684c9fa7acc3e8d0bc989455b5@2x.jpg', 10),
    (3, 'Пицца', 'Ароматная пицца на выбор.', 15000, 'https://mykaleidoscope.ru/x/uploads/posts/2022-09/1663842067_32-mykaleidoscope-ru-p-mini-pitstsa-v-dukhovke-yeda-instagram-40.jpg', 10)
]

cursor.executemany('INSERT INTO products (id, name, description, price, photo, quantity) VALUES (?, ?, ?, ?, ?, ?)', products)
conn.commit()

# Закрываем соединение с базой данных
cursor.close()
conn.close()
