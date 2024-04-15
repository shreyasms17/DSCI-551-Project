# database.py
import sqlite3
import json

def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_products_from_db(db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM products')  # Ensure the table name is correct
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
    cur.execute(f"""INSERT INTO users(username, password, logged_in, admin_user) values ("{user_dict['username']}", 
        "{user_dict['password']}", 0, 0);""")
    conn.commit()
    conn.close()


def login_user(username, db_path):
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
    # cur.execute(f"""select * from session""")
    # a = cur.fetchall()
    # # print(a)
    conn.close()
    print(get_cart(id, db_path))

def update_product(product_dict, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""UPDATE products SET main_category = '{product_dict['main_category']}', 
        sub_category = '{product_dict['sub_category']}',
        link = '{product_dict['link']}',
        discount_price_usd = {product_dict['discount_price_usd']} 
        WHERE name = '{product_dict['name']}' """)
    conn.commit()
    conn.close()


def delete_product_from_db(product_name, db_path):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"""DELETE FROM products WHERE name = '{product_name}'""")
    conn.commit()
    conn.close()


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
