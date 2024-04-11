from flask import render_template
from database import get_products_from_db

# Database paths are defined here
DATABASE_PATH_1 = 'src/data/databases/products_1.db'
DATABASE_PATH_2 = 'src/data/databases/products_2.db'

def init_app(app):
    @app.route('/')
    def product_listings():
        products_1 = get_products_from_db(DATABASE_PATH_1)
        products_2 = get_products_from_db(DATABASE_PATH_2)
        products = products_1 + products_2  # Combine products from both databases
        return render_template('listing.html', products=products)
