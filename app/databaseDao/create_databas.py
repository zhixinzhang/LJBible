import mysql.connector

# MySQL connection parameters
host = 'localhost'
user = 'luke'
password = '123456'
database = 'LJBible'

# Establish a connection to MySQL
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Function to create a database if not exists
def create_database_if_not_exist(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created successfully (if not exists).")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()

# Call the function to create the database
create_database_if_not_exist(conn, 'your_database_name')

# Close the MySQL connection
conn.close()
