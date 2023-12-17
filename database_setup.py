import sqlite3

conn = sqlite3.connect('books.db')

c = conn.cursor()

c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
    )
''')

c.execute('''
    CREATE TABLE books (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        isbn_10 TEXT,
        isbn_13 TEXT,
        title TEXT,
        author TEXT,
        page_count INTEGER,
        average_rating REAL,
        thumbnail TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))

conn.commit()
conn.close()
