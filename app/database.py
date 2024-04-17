import sqlite3
import json
import hashlib

DATABASE_PATH_1 = './data/databases/products_1.db'
DATABASE_PATH_2 = './data/databases/products_2.db'

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

def get_product_from_db(db_path, product_name):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM products WHERE name = "{product_name}" ')  # Ensure the table name is correct
    product = cur.fetchall()
    conn.close()

    if len(product) == 0:
        return None
    else:    
        return product


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


def get_user_from_db(username):
    if len(username) % 2 == 0:
        db_path = DATABASE_PATH_1
    else:
        db_path = DATABASE_PATH_2

    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM users WHERE username = "{username}"')
    user = cur.fetchall()
    conn.close()

    if user:
        return user
    else:
        return None

def add_user_to_db(user_dict):
    if len(user_dict['username']) % 2 == 0:
        db_path = DATABASE_PATH_1
    else:
        db_path = DATABASE_PATH_2

    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO users(id, username, password, logged_in) values ("{hashlib.md5(user_dict['username'].encode()).hexdigest()}", "{user_dict['username']}", 
        "{user_dict['password']}", 0);""")
    conn.commit()
    conn.close()


def login_user(username):
    if len(username) % 2 == 0:
        db_path = DATABASE_PATH_1
    else:
        db_path = DATABASE_PATH_2

    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f""" UPDATE users SET logged_in = 1 WHERE username = '{username}' """)
    conn.commit()
    conn.close()

def save_cart(id, cart, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    print("dumping: ", json.dumps(cart))
    cur.execute(f""" INSERT INTO session (user_id, cart) VALUES (?, ?)""", (id, json.dumps(cart)))
    conn.commit()
    conn.close()
    print(get_cart(id, db_path))

def update_product(product_dict):
    print("product dict inside update_product: " + str(product_dict))
    db_path = get_db_path_for_category(product_dict['main_category'])


    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""UPDATE products SET main_category = '{product_dict['main_category']}', 
        sub_category = '{product_dict['sub_category']}',
        link = '{product_dict['link']}',
        discount_price_usd = {product_dict['discount_price_usd']} 
        WHERE name = '{product_dict['name']}' """)
    conn.commit()
    conn.close()


def add_product_to_db(product_dict):
    category, sub_category = product_dict['category_subcategory'].split("|")
    print("product_dict inside add_product_to_db: " + str(product_dict))
    print("category: " + str(category))
    db_path = get_db_path_for_category(category)
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    cur.execute(f"""
        INSERT INTO products(name, main_category, sub_category, image, link, discount_price_usd)
        VALUES (
            "{product_dict['product_name']}", "{category}", "{sub_category}",
            "{product_dict['image_link']}", "{product_dict['link']}", {product_dict['price']})
    """)

    conn.commit()
    conn.close()



def delete_product_from_db(product_name, category):
    db_path = get_db_path_for_category(category)
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""DELETE FROM products WHERE name = '{product_name}'""")
    conn.commit()
    conn.close()


def get_cart(id, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""select cart from session where user_id = "{id}" """)
    session_info = cur.fetchall()
    print(session_info)
    conn.close()
    if not session_info or not session_info[0]["cart"]:
        return {}
    else:
        return json.loads(session_info[0]['cart'])

def clear_cart(id, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""delete from session where user_id = "{id}" """)
    conn.close()
