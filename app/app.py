from flask import Flask
import routes
from db_setup import *
# import sqlalchemy as db
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET"
 
# LoginManager is needed for our application 
# to be able to log in and out users
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize routes
routes.init_app(app, login_manager)

# Specify the directory containing the CSV files
directory = 'data/raw/'

# Specify the path to the YAML configuration file
config_file = 'config/hash_config.yaml'

# Specify the directory to clean up
database_directory = 'data/databases'

# Call the function to clean up the directory
cleanup_directory(database_directory)

# Call the function to create databases and insert data
create_database_and_insert_data(directory, database_directory, config_file)

# Call the function to read sample data from the databases
read_sample_data(database_directory)

# engine_1 = db.create_engine("sqlite:///data/databases/products_1.db")
# conn_1 = engine_1.connect()

# engine_2 = db.create_engine("sqlite:///data/databases/products_2.db")
# conn_2 = engine_2.connect()
# metadata = db.MetaData() #extracting the metadata

# products_1_table = db.Table('products', metadata, 
# autoload_with=engine_1) #Table object

# products_2_table = db.Table('products', metadata, 
# autoload_with=engine_1) #Table object

# print("MetaData: ")
# print(repr(metadata.tables['products']))
if __name__ == '__main__':
    app.run(debug=True)
