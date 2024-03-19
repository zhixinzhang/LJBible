import mysql.connector
import datetime
import logging

class MySQLBibleDatabase:
    books_table = 'ljbible.books'
    book_contents_table = 'ljbible.book_contents'
    chapters_table = 'ljbible.chapters'
    verses_table = 'ljbible.verses'
    verse_contents_table = 'ljbible.verse_contents'
    comments_table = 'ljbible.comments'
    beads_table = 'ljbible.beads'
    bead_contents_table = 'ljbible.bead_contents'

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

    def insert_book(self, connection, abbrevation_cn, book_name_cn, 
                    abbrevation_eng, book_name_eng, chapter_num, new_or_old, book_type, author):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.books_table} 
                (book_name_cn, abbrevation_cn, book_name_eng, abbrevation_eng, chapter_num, new_or_old, 
                book_type, ac_bc_time, location, author, created_at) 
                VALUES ('{book_name_cn}', '{abbrevation_cn}', '{book_name_eng}', '{abbrevation_eng}', {chapter_num},
                '{new_or_old}', '{book_type}', '', '', '{author}', '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            book_id = cursor.lastrowid
            print("DB Inserting book successfully {} : {}  {} {}".format(book_id, book_name_cn, book_name_eng, chapter_num))
            logging.info("DB Inserting book successfully {} : {}  {} {} ".format(book_id, book_name_cn, book_name_eng, chapter_num))
            return book_id

        except Exception as e:
            print(f"Error executing SQL script: {e}")
            logging.error(f"insert book failed sql :  {sql_script}")

    def insert_book_content(self, connection, book_name_cn, version, descriptions, crawler_link, book_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.book_contents_table} 
                (book_name_cn, version, descriptions, crawler_link, book_id, created_at) 
                VALUES ('{book_name_cn}', '{version}', '{descriptions}', '{crawler_link}', {book_id}, '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            book_content_id = cursor.lastrowid

            print("DB Inserting book content successfully {} : {}  {}".format(book_content_id, book_name_cn, version))
            logging.info("DB Inserting book content successfully {} : {}  {}".format(book_content_id, book_name_cn, version))
            return book_content_id

        except Exception as e:
            print(f"Error executing SQL script: {e}")
            logging.error(f"insert book failed sql :  {sql_script}")

    def insert_chapater(self, connection, chapter_num, body, crawler_link, book_content_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.chapters_table} 
                (chapter_num, body, crawler_link, book_content_id, created_at) 
                VALUES 
                ({chapter_num}, '{body}', '{crawler_link}', {book_content_id}, '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            chapter_id = cursor.lastrowid
            print("DB Insert chapter successfully num : {} : {} ".format(chapter_num, body))
            logging.info("DB Insert chapter successfully num : {} : {} ".format(chapter_num, body))
            return chapter_id

        except Exception as e:
            logging.error("insert chapter failed error :  {}".format(e))
            print(f"Error executing SQL script: {e}")  

    def insert_verse(self, connection, verse_num, verse_level, verse_gold, verse_liked, chapter_num, chapter_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script = f"""
                INSERT INTO {self.verses_table} 
                (verse_num, verse_level, verse_gold, verse_liked, chapter_num, chapter_id, created_at) 
                VALUES 
                ({verse_num}, '{verse_level}', {verse_gold}, {verse_liked}, {chapter_num}, {chapter_id}, '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            verse_id = cursor.lastrowid
            print("DB Inserting verse successfully {} : {}".format(chapter_id, verse_num))
            logging.info("DB Inserting verse successfully {} : {}".format(chapter_id, verse_num))
            return verse_id
        
        except Exception as e:
            print(f"Error executing SQL script: {e}")
            logging.error("Insert verse failed error :  {}".format(e))

    def insert_verse_content(self, connection, original_content, content_with_mark, version, crawler_link, verse_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script_one = "SET FOREIGN_KEY_CHECKS = 0;"
            sql_script_two = f"""
                INSERT INTO {self.verse_contents_table} 
                (original_content, content_with_mark, version, crawler_link, verse_id, created_at) 
                VALUES 
                ("{original_content}", "{content_with_mark}", '{version}',
                '{crawler_link}',  {verse_id}, '{now}');
            """
            sql_script_three = "SET FOREIGN_KEY_CHECKS = 1;"

            cursor.execute(sql_script_one)
            connection.commit()
            cursor.execute(sql_script_two)
            connection.commit()
            content_id = cursor.lastrowid

            cursor.execute(sql_script_three)
            connection.commit()
            
            print("DB Insert verse contents successfully verse_contents_id {} : {}".format(content_id, original_content))
            logging.info("DB Insert verse contents successfully verse_contents_id {} : {}".format(content_id, original_content))
            return content_id

        except Exception as e:
            print(f"Error executing SQL script insert english_verse : {e}") 
            logging.error(f"Error executing SQL script insert english_verse :  {e}")  

    def insert_comment(self, connection, comment_num, mark, original_content, crawler_link, verse_content_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.comments_table} 
                (comment_num, mark, content, verse_content_id, crawler_link, created_at) 
                VALUES 
                ({comment_num}, {mark}, '{original_content}', {verse_content_id}, '{crawler_link}', '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            comment_id = cursor.lastrowid
            print("DB Inserting comment executed successfully comment id is {} : {}".format(comment_id, original_content))
            logging.info("DB Inserting comment executed successfully comment id is {} : {}".format(comment_id, original_content))
            return comment_id
        
        except Exception as e:
            logging.error("Inserting comment failed error :  {}".format(e))
            print(f"Error executing insert_comments SQL script: {e}") 

    def insert_bead(self, connection, bead_num, bead_range, mark, original_content, crawler_link, verse_content_id):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)

            sql_script = f"""
                INSERT INTO {self.beads_table} 
                (bead_num, bead_range, mark, content, verse_content_id, crawler_link, created_at) 
                VALUES 
                ('{bead_num}', '{bead_range}', '{mark}', '{original_content}', {verse_content_id}, '{crawler_link}',  '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            bead_id = cursor.lastrowid
            print("DB Inserting bead executed successfully comment_id : {} bead_id : {}".format(bead_id, original_content ))
            logging.info("DB Inserting bead executed successfully comment_id : {} bead_id : {}".format(bead_id, original_content ))
            return bead_id
        
        except Exception as e:
            print(f"Error executing insert_comments SQL script: {e}")
            logging.error("Inserting bead failed error : {} ".format(e))

    def insert_bead_contents(self, connection, used_cn_abbrevation, used_eng_abbrevation, located_cn_abbrevation, located_eng_abbrevation, 
                             used_chapter_num, used_verse_num, located_chapter_num, located_verse_num, content, original_content, bead_id, 
                             verse_content_id, crawler_link):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor()
            sql_script = f"""
                INSERT INTO {self.bead_contents_table} 
                (used_cn_abbrevation, used_eng_abbrevation, located_cn_abbrevation, located_eng_abbrevation, used_chapter_num,
                  used_verse_num, located_chapter_num, located_verse_num, content, original_content, bead_id, verse_content_id, crawler_link, created_at) 
                VALUES 
                ('{used_cn_abbrevation}', '{used_eng_abbrevation}', '{located_cn_abbrevation}', '{located_eng_abbrevation}',
                  {used_chapter_num}, {used_verse_num}, {located_chapter_num}, {located_verse_num}, '{content}', '{original_content}',
                    {bead_id}, {verse_content_id}, '{crawler_link}', '{now}');
            """
            cursor.execute(sql_script)
            connection.commit()
            bead_content_id = cursor.lastrowid
            print("DB Inserting bead conetnet executed successfully comment_id : {} bead_id : {}".format(bead_content_id, content ))
            logging.info("DB Inserting bead conetnet executed successfully comment_id : {} bead_id : {}".format(bead_content_id, content ))
            return bead_content_id
        
        except Exception as e:
            print(f"Error executing insert_comments SQL script: {e}")        
            logging.error("Inserting bead failed error : {} ".format(e))

    def query_book_by_name(self, connection, name):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script = f"SELECT * FROM {self.books_table}  WHERE book_name = '{name}';"
                
            cursor.execute(sql_script)
            result = cursor.fetchone()
            print("Query books executed successfully book name :  {}, book_id : {}".format(name, result['id']))
            logging.info("Query books executed successfully book name :  {}, book_id : {}".format(name, result['id']))
            return result

        except Exception as e:
            logging.error("insert book failed sql :  {}, {}".format(sql_script, e))
            print("insert book failed sql :  {}, {}".format(sql_script, e))

    def query_book_by_eng_abbreviation_name(self, connection, name):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        try:
            cursor = connection.cursor(buffered=True, dictionary=True)
            sql_script = f"SELECT * FROM {self.books_table}  WHERE book_name_abbreviation_eng = '{name}';"
                
        
            cursor.execute(sql_script)
            result = cursor.fetchone()

            print(f"Query books executed successfully book name :  {name}, book_id : {result['id']}")
            logging.info(f"Query books executed successfully book name :  {name}, book_id : {result['id']}")
            return result

        except Exception as e:
            print(f"Error executing SQL script: {e}")
            logging.error(f"insert book failed sql :  {sql_script}")

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
