import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    """Return a PostgreSQL connection."""
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def setup_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT,
            description TEXT,
            price TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT -1,
            deleted INTEGER DEFAULT 0,
            emoji TEXT DEFAULT ''
        )
    ''')

    # Add emoji column if it doesn't exist (migration for existing DBs)
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN emoji TEXT DEFAULT ''")
    except Exception:
        pass  # Column already exists

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            product_id INTEGER,
            status TEXT,
            receipt_file_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default products if table is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(
            "INSERT INTO products (name, description, price, image_url, stock) VALUES (%s, %s, %s, %s, %s)",
            ('Capcut Pro 1 ខែ', 'គណនី Capcut Pro រយៈពេល 1 ខែ', '$2.00', '', -1)
        )
        cursor.execute(
            "INSERT INTO products (name, description, price, image_url, stock) VALUES (%s, %s, %s, %s, %s)",
            ('Capcut Pro 1 ឆ្នាំ', 'គណនី Capcut Pro រយៈពេល 1 ឆ្នាំ', '$15.00', '', -1)
        )
        cursor.execute(
            "INSERT INTO products (name, description, price, image_url, stock) VALUES (%s, %s, %s, %s, %s)",
            ('Gemini Advanced', 'គណនី Gemini Advanced 1 ខែ', '$3.00', '', -1)
        )

    conn.commit()
    cursor.close()
    conn.close()

def add_user(user_id, username, full_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (user_id, username, full_name) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING',
        (user_id, username, full_name)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, full_name FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, price, image_url, stock, COALESCE(emoji, \'\') as emoji FROM products WHERE deleted = 0')
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products

def get_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description, price, image_url, stock, COALESCE(emoji, '') as emoji FROM products WHERE id = %s AND deleted = 0",
        (product_id,)
    )
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return product

def create_order(user_id, product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO orders (user_id, product_id, status) VALUES (%s, %s, %s) RETURNING id',
        (user_id, product_id, 'pending')
    )
    order_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return order_id

def update_order_receipt(order_id, receipt_file_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE orders SET receipt_file_id = %s, status = %s WHERE id = %s',
        (receipt_file_id, 'paid_pending_approval', order_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def update_order_status(order_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_order(order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.id, o.user_id, p.name, o.status, o.receipt_file_id, p.id
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.id = %s
    ''', (order_id,))
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    return order

# Admin Functions
def add_product(name, description, price, image_url='', stock=-1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO products (name, description, price, image_url, stock) VALUES (%s, %s, %s, %s, %s)',
        (name, description, price, image_url, stock)
    )
    conn.commit()
    cursor.close()
    conn.close()

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET deleted = 1 WHERE id = %s', (product_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return deleted_count > 0

def update_product_price(product_id, price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET price = %s WHERE id = %s', (price, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_product_image(product_id, image_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET image_url = %s WHERE id = %s', (image_url, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_product_stock(product_id, stock):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET stock = %s WHERE id = %s', (stock, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def deduct_stock(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Deduct only if stock > 0. If it's -1 (unlimited), we don't change it.
    cursor.execute('UPDATE products SET stock = stock - 1 WHERE id = %s AND stock > 0', (product_id,))
    conn.commit()
    cursor.close()
    conn.close()

def update_product_name(product_id, new_name):
    """Rename a product."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET name = %s WHERE id = %s', (new_name, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_product_emoji(product_id, emoji):
    """Set or update the emoji for a product."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET emoji = %s WHERE id = %s', (emoji, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_count():
    """Return total number of unique users who have used the bot."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

def get_admins():
    """Return all extra admins (excluding the main owner)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username, added_at FROM admins ORDER BY added_at ASC')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def add_admin(user_id, username=''):
    """Add a new admin. Returns False if already exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO admins (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING',
        (user_id, username)
    )
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0

def remove_admin(user_id):
    """Remove an admin by user_id. Returns False if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE user_id = %s', (user_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return affected > 0

def is_admin(user_id):
    """Check if a user_id exists in the admins table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM admins WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None
