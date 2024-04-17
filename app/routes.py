from flask import render_template, request, redirect, url_for, abort, session
from database import get_products_from_db, get_user_from_db, add_user_to_db, login_user, DATABASE_PATH_1, \
    DATABASE_PATH_2, get_all_categories, \
    get_products_from_category, get_cart, save_cart, clear_cart

def hash_user(username):
    if len(username)%2==0:
        return DATABASE_PATH_1
    else:
        return DATABASE_PATH_2


def init_app(app, login_manager):
    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route('/listings', methods=['GET'])
    def product_listings():
        user_id = session['id']
        # Get all categories from both databases
        categories_1 = get_all_categories(DATABASE_PATH_1)
        categories_2 = get_all_categories(DATABASE_PATH_2)
        all_categories = sorted(set(categories_1 + categories_2))

        # Retrieve the category and search query from request parameters
        selected_category = request.args.get('category', '')
        search_query = request.args.get('search', '')

        # Initially fetch products from both databases
        products = get_products_from_db(DATABASE_PATH_1) + get_products_from_db(DATABASE_PATH_2)
        products = filter_products(products)  # Filter out invalid products

        # If a specific category is selected, fetch products from the corresponding database
        if selected_category:
            products = get_products_from_category(selected_category)
            products = filter_products(products)  # Filter again after fetching by category

        # If a search query is provided, further filter the products
        if search_query:
            products = [product for product in products if search_query.lower() in product['name'].lower()]

        return render_template('listing.html', products=products, categories=all_categories,
                               selected_category=selected_category, user_id=user_id)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        # If a post request was made, find the user by
        # filtering for the username
        if request.method == "POST":
            user = get_user_from_db(request.form.get("username"), hash_user(request.form.get("username")))
            # Check if the password entered is the
            # same as the user's password
            print("User: " + str(user))
            # print(dict(user[0]))
            if user and user[0]["password"] == request.form.get("password"):
                # Use the login_user method to log in the user
                login_user(user[0]["username"], hash_user(user[0]["username"]))
                # retrieve cart info
                session['cart'] = get_cart(user[0]['id'], hash_user(user[0]["username"]))
                session['id'] = user[0]['id']
                return redirect(url_for("product_listings"))
            else:
                abort(404)
            # Redirect the user back to the home
            # (we'll create the home route in a moment)
        else:
            return render_template("login.html")

    @app.route('/signup', methods=["GET", "POST"])
    def register():
        # If the user made a POST request, create a new user
        if request.method == "POST":
            user_dict = {
                'username': request.form.get("username"),
                'password': request.form.get("password")
            }
            # Add the user to the database
            add_user_to_db(user_dict, hash_user(user_dict['username']))

            return redirect(url_for("login"))
        # Renders sign_up template if user made a GET request
        return render_template("signup.html")

    # Creates a user loader callback that returns the user object given an id
    @login_manager.user_loader
    def loader_user(user_id):
        user_1 = get_user_from_db(user_id, DATABASE_PATH_1)
        if user_1:
            return user_1
        else:
            return get_user_from_db(user_id, DATABASE_PATH_2)

    @app.route('/add_to_cart', methods=['POST'])
    def add_to_cart():
        data = request.get_json()
        price = data['price']
        product_name = data['productName']
        if 'cart' not in session:
            session['cart'] = {}
        session['cart'][product_name] = session['cart'].get(product_name, {"qty": 0, "price": price})
        session['cart'][product_name]['qty'] += 1
        session['cart'][product_name]['price'] = price
        print(session)
        session.modified = True
        return redirect(url_for('product_listings'))

    @app.route('/cart/<user_id>')
    def show_cart(user_id):
        cart_details = []
        total_price = 0
        # print("ID: ", session.get('id', -1), session, user_id)
        if user_id and session.get('id', '') == user_id:
            # print("EQUALL!!")
            cart_items = session.get('cart', {})
            # print(session.get('cart', {}))
            for product in cart_items:
                if cart_items[product]["qty"] > 0:
                    cart_details.append(
                        {"name": product, "qty": cart_items[product]["qty"], "price": cart_items[product]["price"]})
                    total_price += cart_items[product]["qty"] * float(cart_items[product]["price"])
            # print("Cart details", cart_details)
        return render_template('cart.html', user_id=session.get('id'), cart=cart_details, total_price=total_price)

    @app.route('/logout')
    def logout():
        # save cart info to db
        user_1 = get_user_from_db(session['id'], DATABASE_PATH_1)
        if user_1:
            if session.get('cart', {}):
                save_cart(session['id'], session['cart'], DATABASE_PATH_1)
        else:
            if session.get('cart', {}):
                save_cart(session['id'], session['cart'], DATABASE_PATH_2)
        session.pop('cart', None)
        return redirect(url_for('login'))

    @app.route('/modify_quantity', methods=['POST'])
    def modify_quantity():
        data = request.get_json()
        product_name = data["productName"]
        session['cart'][product_name]['qty'] = data['qty']
        if session['cart'][product_name]['qty'] == 0:
            del session['cart'][product_name]
        session.modified = True
        return {
            "success": True
        }
    
    @app.route('/place_order', methods=['POST'])
    def place_order():
        data = request.get_json()
        user_id = data["user_id"]
        response = {
            "text" : ''
        }
        if session.get('cart', {}) and session.get('id', '') == user_id:
            session.pop('cart', None)
            response['text'] = "Order placed!"
        else:
            response['text'] = "Nothing in cart!"
        clear_cart(user_id, DATABASE_PATH_1)
        session.modified = True
        return response


def filter_products(products):
    valid_products = []
    for product in products:
        # Check if the product's price is not None
        if product[7] is not None:
            valid_products.append(product)

    print(f"Filtered products count: {len(valid_products)}")  # Debugging output
    return valid_products