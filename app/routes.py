from flask import render_template, request, redirect, url_for, abort
from database import get_products_from_db, get_user_from_db, add_user_to_db, login_user

# Assume the database paths are imported or defined here
DATABASE_PATH_1 = 'data/databases/products_1.db'
DATABASE_PATH_2 = 'data/databases/products_2.db'

def init_app(app, login_manager):
    @app.route('/')
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
