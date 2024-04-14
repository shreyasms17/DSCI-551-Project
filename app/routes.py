from flask import request, render_template
from database import get_products_from_db, DATABASE_PATH_1, DATABASE_PATH_2, get_all_categories, \
    get_products_from_category


def init_app(app):
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
