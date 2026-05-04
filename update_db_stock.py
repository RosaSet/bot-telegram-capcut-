import sqlite3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE products ADD COLUMN stock INTEGER DEFAULT -1")
    print("Added stock column. (-1 means unlimited/untracked for now)")
except sqlite3.OperationalError as e:
    print(f"OperationalError: {e}")
conn.commit()
conn.close()
