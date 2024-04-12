import sqlite3

# Create a connection to the orders database
conn_orders = sqlite3.connect('orders.db')
cursor_orders = conn_orders.cursor()

# Create the 'orders' table with an auto-incrementing 'order_id' column
cursor_orders.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        surname TEXT,
        name TEXT,
        patronymic TEXT,
        price REAL,
        time TEXT,
        products TEXT,
        status_send_to_admin INTEGER,
        status_get_order INTEGER
    )
    
''')

# Close the cursor and connection to the orders database
cursor_orders.close()
conn_orders.close()
