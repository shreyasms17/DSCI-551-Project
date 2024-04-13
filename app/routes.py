from flask import render_template, request, redirect, url_for, abort, session
from database import get_products_from_db, get_user_from_db, add_user_to_db, login_user, get_cart, save_cart

# Assume the database paths are imported or defined here
DATABASE_PATH_1 = 'data/databases/products_1.db'
DATABASE_PATH_2 = 'data/databases/products_2.db'

def init_app(app, login_manager):
    @app.route("/")
    def index():
        return redirect(url_for("login"))
    
    @app.route('/listings')
    def product_listings():
        products_1 = get_products_from_db(DATABASE_PATH_1)
        products_2 = get_products_from_db(DATABASE_PATH_2)
        products = products_1 + products_2  # Combine products from both databases
        return render_template('listing.html', products=products)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        # If a post request was made, find the user by 
        # filtering for the username
        if request.method == "POST":
            user = get_user_from_db(request.form.get("username"), DATABASE_PATH_1)
            # Check if the password entered is the 
            # same as the user's password
            print("User: " + str(user))
            # print(dict(user[0]))
            if user and user[0]["password"] == request.form.get("password"):
                # Use the login_user method to log in the user
                login_user(user[0]["username"], DATABASE_PATH_1)
                # retrieve cart info
                session['cart'] = get_cart(user[0]['id'], DATABASE_PATH_1)
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
            add_user_to_db(user_dict, DATABASE_PATH_1)

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
    
    @app.route('/add_to_cart/<product_name>', methods=['POST'])
    def add_to_cart(product_name):
        data = request.get_json()
        price = data['price']
        if 'cart' not in session:
            session['cart'] = {}
        session['cart'][product_name] = session['cart'].get(product_name, {"qty": 0, "price": price})
        session['cart'][product_name]['qty'] += 1
        session['cart'][product_name]['price'] = price
        print(session)
        session.modified = True
        return redirect(url_for('product_listings'))
    
    @app.route('/cart')
    def show_cart():
        cart_items = session.get('cart', {})
        # print(cart_items)
        cart_details = []
        total_price = 0
        for product in cart_items:
            cart_details.append({"name": product, "qty": cart_items[product]["qty"], "price": cart_items[product]["price"]})
            total_price +=  cart_items[product]["qty"] * float(cart_items[product]["price"])
        print(cart_details)
        return render_template('cart.html', cart=cart_details, total_price=total_price)
    
    @app.route('/logout')
    def logout():
        # save cart info to db
        save_cart(session['id'], session['cart'], DATABASE_PATH_1)
        session.pop('cart', None)
        return redirect(url_for('login'))
