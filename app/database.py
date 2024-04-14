import sqlite3

DATABASE_PATH_1 = 'src/data/databases/products_1.db'
DATABASE_PATH_2 = 'src/data/databases/products_2.db'

# Dictionary to map categories to their respective databases
CATEGORY_HASH = {
    'home & kitchen': DATABASE_PATH_1,
    'tv, audio & cameras': DATABASE_PATH_1,
    'accessories': DATABASE_PATH_2,
    'beauty & health': DATABASE_PATH_2,
    'grocery & gourmet foods': DATABASE_PATH_2
}


def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_products_from_db(db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM products')
    products = cur.fetchall()
    conn.close()
    return products


def get_all_categories(db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT main_category FROM products')
    categories = cur.fetchall()
    conn.close()
    return [category[0] for category in categories]


def get_products_from_category(category):
    db_path = get_db_path_for_category(category)
    if db_path is None:
        return []  # Return empty list if no matching database is found

    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM products WHERE main_category = ?', (category,))
    products = cur.fetchall()
    conn.close()
    return products


def get_db_path_for_category(category):
    """Returns the database path based on the category using a hash function (dictionary lookup)."""
    return CATEGORY_HASH.get(category, None)
