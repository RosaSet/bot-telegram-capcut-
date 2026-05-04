import sqlite3

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE products ADD COLUMN image_url TEXT")
    print("Added image_url column.")
except sqlite3.OperationalError as e:
    print(f"OperationalError: {e} (Maybe column already exists?)")
conn.commit()
conn.close()
