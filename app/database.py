import sqlite3
import json

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


def get_user_from_db(username, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM users WHERE username = "{username}"')
    user = cur.fetchall()
    conn.close()

    if user:
        return user
    else:
        return None

def add_user_to_db(user_dict, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO users(username, password, logged_in) values ("{user_dict['username']}", 
        "{user_dict['password']}", 0);""")
    conn.commit()
    conn.close()


def login_user(username, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f""" UPDATE users SET logged_in = 1 WHERE username = '{username}' """)
    conn.close()

def save_cart(id, cart, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    print("dumping: ", json.dumps(cart))
    cur.execute(f""" INSERT INTO session (user_id, cart) VALUES (?, ?)""", (id, json.dumps(cart)))
    conn.commit()
    # cur.execute(f"""select * from session""")
    # a = cur.fetchall()
    # # print(a)
    conn.close()
    print(get_cart(id, db_path))

def get_cart(id, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""select cart from session where user_id = {id}""")
    session_info = cur.fetchall()
    print(session_info)
    conn.close()
    if not session_info or not session_info[0]["cart"]:
        return {}
    else:
        return json.loads(session_info[0]['cart'])