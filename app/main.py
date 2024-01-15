
from databaseDao import MySQLBibleDatabase as DB

def main():
    bDB = DB.MySQLBibleDatabase(host="localhost", user="luke", password="123456", database="ljbible")
    print("hello world!")

if __name__ == '__main__':
    main()