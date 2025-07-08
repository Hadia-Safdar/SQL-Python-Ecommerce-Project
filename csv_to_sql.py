import pandas as pd
import mysql.connector
import os

# List of CSV files and their corresponding table names
csv_files = [
    ('customers.csv', 'customers'),
    ('orders.csv', 'orders'),
    ('sellers.csv', 'sellers'),
    ('products.csv', 'products'),
    ('geolocation.csv', 'geolocation'),
    ('payments.csv', 'payments'),
    ('order_items.csv', 'order_items')  
]

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost',  
    user='root',
    password='your_password',
    database='ecommerce'
)
cursor = conn.cursor()

# Folder containing the CSV files
folder_path = r'E:\Ecommerce' 

# Function to map pandas dtypes to SQL data types
def get_sql_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'DATETIME'
    else:
        return 'TEXT'

# Loop through each CSV file
for csv_file, table_name in csv_files:
    file_path = os.path.join(folder_path, csv_file)

    # Read CSV into DataFrame
    df = pd.read_csv(file_path)

 # Replace NaN with None for SQL compatibility
    df = df.where(pd.notnull(df), None)

    # Clean column names
    df.columns = [col.strip().replace(' ', '_').replace('-', '_').replace('.', '_') for col in df.columns]

    # Create SQL CREATE TABLE query dynamically
    columns = ', '.join([f'`{col}` {get_sql_type(df[col].dtype)}' for col in df.columns])
    create_table_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns})'
    cursor.execute(create_table_query)

    # Insert each row into the table
    for _, row in df.iterrows():
        values = tuple(None if pd.isna(x) else x for x in row)
        insert_query = f"INSERT INTO `{table_name}` ({', '.join(['`' + col + '`' for col in df.columns])}) VALUES ({', '.join(['%s'] * len(row))})"
        cursor.execute(insert_query, values)

    # Commit after each file
    conn.commit()
    print(f"{table_name} uploaded successfully.")

# Close the database connection
conn.close()
print(" All files uploaded to MySQL successfully.")
