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