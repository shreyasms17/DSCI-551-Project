from flask import render_template, request, redirect, url_for, abort
from database import get_products_from_db, get_user_from_db, add_user_to_db, login_user 
from database import get_product_from_db, update_product, delete_product_from_db

# Assume the database paths are imported or defined here
DATABASE_PATH_1 = 'data/databases/products_1.db'
DATABASE_PATH_2 = 'data/databases/products_2.db'

def init_app(app, login_manager):
    @app.route('/')
    def product_listings():
        products_1 = get_products_from_db(DATABASE_PATH_1)
        products_2 = get_products_from_db(DATABASE_PATH_2)
        products = products_1 + products_2  # Combine products from both databases
        return render_template('listing.html', products=products, is_admin=True)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        # If a post request was made, find the user by 
        # filtering for the username
        if request.method == "POST":
            user = get_user_from_db(request.form.get("username"), DATABASE_PATH_1)
            # Check if the password entered is the 
            # same as the user's password
            print("User: " + str(user))
            if user and user[0]["password"] == request.form.get("password"):
                # Use the login_user method to log in the user
                login_user(user[0]["username"], DATABASE_PATH_1)
                return redirect("/")
            else:
                abort(404)
            # Redirect the user back to the home
            # (we'll create the home route in a moment)
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


    @app.route('/admin/products', methods=["GET", "POST"])
    def products():
      # If the user made a POST request, create a new user
        if request.method == "GET":
            product_name = request.args.get("product_name")
            product = get_product_from_db(DATABASE_PATH_1, product_name)


            if not product:
                product = get_product_from_db(DATABASE_PATH_2, product_name)

            return render_template("product.html", product=product[0])
        elif request.method == "POST":
            product_name = request.form.get("product_name")
            product = get_product_from_db(DATABASE_PATH_1, product_name)
            db_path = DATABASE_PATH_1
            if not product:
                product = get_product_from_db(DATABASE_PATH_2, product_name)
                db_path = DATABASE_PATH_2

            updated_product = request.form
            updated_product_dict = dict(product[0])

            if len(updated_product.get("category_subcategory")) > 0:
                updated_product_dict['main_category'], updated_product_dict['sub_category'] = updated_product.get("category_subcategory").split("|")

            if len(updated_product.get("price")) > 0:
                updated_product_dict['discount_price_usd'] = updated_product.get("price")

            if len(updated_product.get("link")) > 0:
                updated_product_dict['link'] = updated_product.get("link")

            update_product(updated_product_dict, db_path)
            product = get_product_from_db(db_path, product_name)

            return render_template("product.html", product=product[0])

    @app.route('/admin/products/delete', methods=["POST"])
    def delete_product():
        if request.method == "POST":
            product_name = request.form.get("product_name")
            product = get_product_from_db(DATABASE_PATH_1, product_name)
            db_path = DATABASE_PATH_1
            if not product:
                product = get_product_from_db(DATABASE_PATH_2, product_name)
                db_path = DATABASE_PATH_2

            delete_product_from_db(product_name, db_path)
            return redirect("/")
