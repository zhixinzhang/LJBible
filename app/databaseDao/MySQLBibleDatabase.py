import mysql.connector
import datetime
import logging

class MySQLBibleDatabase:
    books_table = 'ljbible.books'
    chapters_table = 'ljbible.chapters'
    verses_table = 'ljbible.verses'
    verse_contents_table = 'ljbible.verse_contents'
    comments_table = 'ljbible.comments'
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
            for table in tables:
                table_names.append('ljbible.' + table['Tables_in_ljbible'])
            
            table_names = ', '.join(table_names)
            print("Contents of s : ", table_names)
            cursor.execute(f"DROP TABLE {table_names}")
            print(f"Table {table_names} dropped successfully")

            connection.commit()

        except Exception as e:
            print(f"Error dropping tables: {e}")

        finally:
            cursor.close()            

    def execute_sql_file(self, file_path, connection):
        cursor = connection.cursor(dictionary=True)

        try:
            # Read SQL file
            with open(file_path, 'r') as sql_file:
                sql_script = sql_file.read()
                sql_commands = sql_script.split(';')

                for command in sql_commands:
                    if command.strip():  # Check if the command is not empty
                        cursor.execute(command)
            # Execute SQL script
            # cursor.execute(sql_script)
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

    def insert_book(self, connection, book_name, book_name_abbreviation, book_name_eng, book_name_abbreviation_eng, new_or_old, book_type, version, author, url):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.books_table} 
                (book_name, book_name_abbreviation, book_name_eng, book_name_abbreviation_eng, ezoe_link, created_at) 
                VALUES ('{book_name}', '{book_name_abbreviation}', '{book_name_eng}', '{book_name_abbreviation_eng}', 
                '{new_or_old}', '{book_type}', '{version}', '{url}', '{author}', '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            book_id = cursor.lastrowid
            print(f"insert books executed successfully book name :  {book_name}, book_id : {book_id}")
            logging.info(f"insert books executed successfully book name :  {book_name}, book_id : {book_id}")
            return book_id

        except Exception as e:
            print(f"Error executing SQL script: {e}")
            logging.error(f"insert book failed sql :  {sql_script}")

    def insert_verse(self, connection, verse_num, verse_level, verse_gold, verse_liked, chapter_number, chapter_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script = f"""
                INSERT INTO {self.verses_table} 
                (verse_num, verse_level, verse_gold, verse_liked, chapter_number, chapter_id, created_at) 
                VALUES 
                ({verse_num}, '{verse_level}', {verse_gold}, {verse_liked}, {chapter_number}, {chapter_id}, '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            verse_id = cursor.lastrowid
            print("Inserting verse successfully {} : {}".format(chapter_id, verse_num))
            logging.info("Inserting verse successfully {} : {}".format(chapter_id, verse_num))
            return verse_id
        
        except Exception as e:
            print(f"Error executing SQL script: {e}")
            logging.error("Insert verse failed error :  {}".format(e))

    def insert_verse_content(self, connection, content, content_with_mark, version, current_url, verse_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script_one = "SET FOREIGN_KEY_CHECKS = 0;"
            sql_script_two = f"""
                INSERT INTO {self.verse_contents_table} 
                (original_content, content_with_mark, version, ezoe_link, verse_id, created_at) 
                VALUES 
                ("{content}", "{content_with_mark}", '{version}',
                '{current_url}',  {verse_id}, '{now}');
            """
            sql_script_three = "SET FOREIGN_KEY_CHECKS = 1;"

            cursor.execute(sql_script_one)
            connection.commit()
            cursor.execute(sql_script_two)
            connection.commit()
            content_id = cursor.lastrowid

            cursor.execute(sql_script_three)
            connection.commit()
            
            print(f"Insert verse contents successfully verse_contents_id : {content_id} : {content}")
            logging.info(f"Insert verse contents successfully verse_contents_id : {content_id} : {content}")
            return content_id

        except Exception as e:
            print(f"Error executing SQL script insert english_verse : {e}") 
            logging.error(f"Error executing SQL script insert english_verse :  {e}")

    def insert_chapater(self, connection, chapter_num, body, ezoe_link, book_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.chapters_table} 
                (chapter_num, body, ezoe_link, book_id, created_at) 
                VALUES 
                ({chapter_num}, '{body}', '{ezoe_link}', {book_id}, '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            chapter_id = cursor.lastrowid
            print("Insert chapter successfully num : {} : {} ".format(chapter_num, body))
            logging.info("Insert chapter successfully num : {} : {} ".format(chapter_num, body))
            return chapter_id

        except Exception as e:
            logging.error("insert chapter failed error :  {}".format(e))
            print(f"Error executing SQL script: {e}")    

    def insert_comment(self, connection, comment_num, mark, original_content, ezoe_link, verse_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.comments_table} 
                (comment_num, mark, content, verse_id, ezoe_link, created_at) 
                VALUES 
                ({comment_num}, {mark}, '{original_content}', {verse_id}, '{ezoe_link}', '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            comment_id = cursor.lastrowid
            print("Inserting comment executed successfully comment id is {} : {}".format(comment_id, original_content))
            logging.info("Inserting comment executed successfully comment id is {} : {}".format(comment_id, original_content))
            return comment_id
        
        except Exception as e:
            logging.error("Inserting comment failed error :  {}".format(e))
            print(f"Error executing insert_comments SQL script: {e}") 

    def insert_bead(self, connection, bead_num, mark, original_content, ezoe_link, verse_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.beads_table} 
                (bead_num, mark, content, verse_id, ezoe_link, created_at) 
                VALUES 
                ('{bead_num}', '{mark}', '{original_content}', {verse_id}, '{ezoe_link}',  '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            comment_id = cursor.lastrowid
            print("Inserting bead executed successfully comment_id : {} bead_id : {}".format(comment_id,original_content ))
            logging.info("Inserting bead executed successfully comment_id : {} bead_id : {}".format(comment_id,original_content ))
            return comment_id
        
        except Exception as e:
            logging.error("Inserting bead failed error : {} ".format(e))
            print(f"Error executing insert_comments SQL script: {e}")      

    def query_book_by_name(self, connection, name):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            # cursor = connection.cursor()
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script = f"SELECT * FROM {self.books_table}  WHERE book_name = '{name}';"
                
        
            cursor.execute(sql_script)
            result = cursor.fetchone()

            print(f"Query books executed successfully book name :  {name}, book_id : {result['id']}")
            logging.info(f"Query books executed successfully book name :  {name}, book_id : {result['id']}")
            return result

        except Exception as e:
            logging.error(f"insert book failed sql :  {sql_script}")
            print(f"Error executing SQL script: {e}")

    def query_verse(self, connection, book_id, chapter_num, verse_num):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)

            sql_script = f"""
                SELECT * FROM {self.verses_table}  as v 
                left join {self.chapters_table} as c 
                on v.chapter_id = c.id 
                left join {self.books_table} as b
                on c.book_id = b.id
                where v.verse_num = {verse_num} and b.id = {book_id} and c.chapter_num = {chapter_num};
            """
        
            cursor.execute(sql_script)
            result = cursor.fetchone()
            cursor.close()

            print(f"Query book executed successfully book name :  {result['book_name']}, book_id : {result['id']}")
            logging.info(f"Query book executed successfully book name :  {result['book_name']}, book_id : {result['id']}")
            return result

        except Exception as e:
            logging.error(f"Error executing SQL script:  {e}")
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
