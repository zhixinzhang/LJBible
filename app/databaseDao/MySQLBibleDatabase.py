import mysql.connector
import logging

class MySQLBibleDatabase:
    book_table = 'ljbible.books'
    chapter_table = 'ljbible.chapters'
    verse_table = 'ljbible.verses'
    comment_table = 'ljbible.comments'
    beads_table = 'ljbible.beads'

    logging.basicConfig(filename='crawler.log', filemode='w', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO) 


    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def drop_all_tables(self, connection):
        cursor = connection.cursor(dictionary=True)

        try:
            # Get the list of tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = []
            # Drop each table
            for table in tables:
                table_names.append('ljbible.' + table['Tables_in_ljbible'])
                # table_names = table['Tables_in_ljbible']
            
            table_names = ', '.join(table_names)
            print("Contents of s : ", table_names)
            cursor.execute(f"DROP TABLE {table_names}")
            print(f"Table '{table_names}' dropped successfully")

            connection.commit()

        except Exception as e:
            print(f"Error dropping tables: {e}")

        finally:
            cursor.close()            

    def execute_sql_file(self, file_path, connection):
        cursor = connection.cursor()

        try:
            # Read SQL file
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()

            # Execute SQL script
            cursor.execute(sql_script)
            connection.commit()
            print("SQL script executed successfully")

        except Exception as e:
            print(f"Error executing SQL script: {e}")

        finally:
            cursor.close()

    def initial_db(self, file_path, connection):
        print("initialing table")
        self.execute_sql_file(file_path, connection)

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            print("Disconnected from the database")

    def insert_book(self, connection, full_book_name, abbrevation, url):
        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.book_table} 
                (book_name, book_name_abbreviation, ezoe_link) 
                VALUES ('{full_book_name}', '{abbrevation}', '{url}');
            """
            cursor.execute(sql_script)
            connection.commit()
            book_id = cursor.lastrowid
            print(f"insert books executed successfully book name :  {full_book_name}, book_id : {book_id}")
            logging.info(f"insert books executed successfully book name :  {full_book_name}, book_id : {book_id}")
            return book_id

        except Exception as e:
            logging.error(f"insert book failed sql :  {sql_script}")
            print(f"Error executing SQL script: {e}")

    def insert_verses(self, connection, verse_num, original_content, content_with_mark, 
                      version, author, ezoe_link, chapater_number, chapter_id):
        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.verse_table} 
                (verse_num, original_content, content_with_mark, version, author, ezoe_link, chapater_number, chapater_id) 
                VALUES 
                ({verse_num}, '{original_content}', '{content_with_mark}', '{version}', '{author}', 
                '{ezoe_link}', '{chapater_number}', {chapter_id});
            """
            cursor.execute(sql_script)
            connection.commit()
            verse_id = cursor.lastrowid
            print(f"insert verse executed successfully verse id is  :  {verse_id}, {original_content}")
            logging.info(f"insert verse executed successfully verse id is  :  {verse_id}, {original_content}")
            return verse_id
        
        except Exception as e:
            print(f"Error executing SQL script: {e}") 

    def insert_chapater(self, connection, chapter_num, body, ezoe_link, book_id):
        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.chapter_table} 
                (chapter_num, body, ezoe_link, book_id) 
                VALUES 
                ({chapter_num}, '{body}', '{ezoe_link}', {book_id});
            """
            cursor.execute(sql_script)
            connection.commit()
            chapter_id = cursor.lastrowid
            print(f"insert chapter executed successfully chapter number is :  {chapter_num}, chapter id is : {chapter_id}")
            logging.info(f"insert chapter executed successfully chapter number is :  {chapter_num}, chapter id is : {chapter_id}")
            return chapter_id

        except Exception as e:
            print(f"Error executing SQL script: {e}")            

    def execute_query(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            self.connection.commit()
            print("Query executed successfully")

        except mysql.connector.Error as err:
            self.connection.rollback()
            print(f"Error executing query: {err}")

    def fetch_data(self, query, data=None):
        try:
            self.cursor.execute(query, data)
            result = self.cursor.fetchall()
            return result

        except mysql.connector.Error as err:
            print(f"Error fetching data: {err}")
            return None

# Example usage
if __name__ == "__main__":
    # Replace these values with your MySQL server details
    db = MySQLBibleDatabase(host="localhost", user="luke", password="123456", database="ljbible")

    db.connect()

    # Example: creating a table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS example_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        age INT
    )
    """
    db.execute_query(create_table_query)

    # Example: inserting data
    insert_data_query = "INSERT INTO example_table (name, age) VALUES (%s, %s)"
    data_to_insert = ("John Doe", 25)
    db.execute_query(insert_data_query, data_to_insert)

    # Example: fetching data
    select_data_query = "SELECT * FROM example_table"
    result = db.fetch_data(select_data_query)
    print("Data from the table:")
    for row in result:
        print(row)

    db.disconnect()
