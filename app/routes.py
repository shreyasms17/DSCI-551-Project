from flask import render_template, request, redirect, url_for, abort
from database import get_products_from_db, get_user_from_db, add_user_to_db, login_user, DATABASE_PATH_1, DATABASE_PATH_2, get_all_categories, \
    get_products_from_category

def init_app(app, login_manager):
    @app.route('/', methods=['GET'])
    def product_listings():
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
                               selected_category=selected_category)


def filter_products(products):
    valid_products = []
    for product in products:
        # Check if the product's price is not None
        if product[7] is not None:
            valid_products.append(product)

    print(f"Filtered products count: {len(valid_products)}")  # Debugging output
    return valid_products

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
