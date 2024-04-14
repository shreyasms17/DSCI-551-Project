import os
import pandas as pd
import numpy as np
import sqlite3
import yaml
import shutil
import random



def cleanup_directory(directory):
    """Clean up a directory if it exists"""
    if os.path.exists(directory):
        shutil.rmtree(directory)
        print(f"Directory '{directory}' cleaned up successfully.")
    else:
        print(f"Directory '{directory}' does not exist.")


def convert_to_usd(price):
    """Convert price from INR to USD"""
    numeric_price = str(price).replace('₹', '').replace(',', '')
    return float(numeric_price) * 0.014

def process_csv_file(csv_file):
    """Process a single CSV file"""
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Randomly select 200 records
    random_records = df.sample(n=min(200, len(df)), random_state=42)

    # Convert discount_price and actual_price columns from INR to USD
    random_records['discount_price_usd'] = random_records['discount_price'].apply(convert_to_usd)
    random_records['actual_price_usd'] = random_records['actual_price'].apply(convert_to_usd)

    # Drop discount_price and actual_price columns
    random_records.drop(columns=['discount_price', 'actual_price'], inplace=True)

    return random_records

def create_database_and_insert_data(directory, database_directory, config_file):
    """Create SQLite databases, connect to them, and insert data"""
    # Load YAML configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    if not os.path.exists(database_directory):
        os.makedirs(database_directory)

    # Process each category
    for category, database_name in config.items():
        # Connect to SQLite database
        db_path = os.path.join(database_directory, f'{database_name}.db')
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = 1")  # Enable foreign key constraints
        conn.execute("CREATE TABLE IF NOT EXISTS products (name TEXT, main_category TEXT, sub_category TEXT, image TEXT, link TEXT, ratings FLOAT, no_of_ratings INTEGER, discount_price_usd REAL, actual_price_usd REAL)")

        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL, 
                logged_in INTEGER
            );
            '''
        )

        # conn.execute("DROP TABLE IF EXISTS session;")
        conn.execute('''
            CREATE TABLE IF NOT EXISTS session (
                user_id INTEGER PRIMARY KEY,
                cart TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            '''
        )

        c = conn.cursor()

        # Iterate over each file in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.csv') and category in filename:
                csv_file = os.path.join(directory, filename)
                # Process the CSV file
                random_records = process_csv_file(csv_file)

                # Convert DataFrame to SQLite table
                random_records.to_sql('products', conn, if_exists='append', index=False)

        # Add indices to product name, main category, subcategory, and price columns
        c.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON products (name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_main_category ON products (main_category)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sub_category ON products (sub_category)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_price ON products (discount_price_usd)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_username ON users (username)")

        # Commit changes and close connection
        conn.commit()
        conn.close()



def read_sample_data(database_directory):
    # Process each category
    for db in os.listdir(database_directory):
        # Connect to SQLite database
        db_path = os.path.join(database_directory, db)
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            # Execute SELECT query to retrieve sample data
            c.execute("SELECT * FROM products LIMIT 5")  # Fetching 5 sample records
            sample_data = c.fetchall()

            for row in sample_data:
                print(row)
            print()

            # Close connection
            conn.close()
        else:
            print(f"Database file not found.")