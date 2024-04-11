from flask import render_template
from database import get_products_from_db

# Assume the database paths are imported or defined here
DATABASE_PATH_1 = '/Users/preetigoel/Documents/GitHub/DSCI-551-Project/src/data/databases/products_1.db'
DATABASE_PATH_2 = '/Users/preetigoel/Documents/GitHub/DSCI-551-Project/src/data/databases/products_2.db'

def init_app(app):
    @app.route('/')
    def product_listings():
        products_1 = get_products_from_db(DATABASE_PATH_1)
        products_2 = get_products_from_db(DATABASE_PATH_2)
        products = products_1 + products_2  # Combine products from both databases
        return render_template('listing.html', products=products)
