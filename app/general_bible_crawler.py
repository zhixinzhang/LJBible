import requests
import random
import time
import logging

from bs4 import BeautifulSoup
from databaseDao import MySQLBibleDatabase as DB

visited_urls = set()
ezoe_url = 'https://ezoe.work/bible/jw/'
books_url_to_crawl = 'https://ezoe.work/bible8/index.html'
chapters_url_to_crawl = 'https://ezoe.work/bible8/'

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO) 
  
bDB = DB.MySQLBibleDatabase(host="localhost", user="luke", password="123456", database="ljbible")
bDB.connect()
bDB.drop_all_tables(bDB.connection)
bDB.initial_db('app/sql/ljbible.sql', bDB.connection)
bDB.connect()
connection = bDB.connection

def books_crawler(url):
    books_abbrevation_crawl(connection, url)

def books_abbrevation_crawl(connection, current_url):
    try:
        soup = ezoe_url_request(current_url)
        books_name_abrevations = soup.find_all('a', attrs={'class':'page-navi'})
        for line in books_name_abrevations:
            time.sleep(random.randint(1, 4))
            abbrevation = line.text
            url = line.attrs['href']
            next_url = chapters_url_to_crawl + url
            logging.info(f"crawling bible books %s", abbrevation)
            chapters_crawler(connection, next_url, abbrevation)

    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def chapters_crawler(connection, current_url, abbrevation):
    try:
        soup = ezoe_url_request(current_url)
        
        full_book_name = soup.find_all('h3')[0].text
        bDB.insert_book(connection, full_book_name, abbrevation, current_url)

        chapters = soup.find_all('a', attrs={'class':'page-navi'})
        for line in chapters:
            chapter = line.text
            logging.info( 'crawling ' + full_book_name +  chapter)
            if not chapter.isdigit():
                logging.error( 'crawling wrong' + full_book_name +  chapter)
                continue

            url = line.attrs['href']
            full_chapter_url = chapters_url_to_crawl + url
            chapter_number = int(chapter) 
            verses_crawler(connection, full_chapter_url, chapter_number, full_book_name)
                                
    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def verses_crawler(connection, current_url, chapter_number, full_book_name):
    try:
        logging.info( "Crawling %s  %s  %s", full_book_name, chapter_number, current_url)

        soup = ezoe_url_request(current_url)
        # chapter_number = soup.find_all('h2', attrs={'class' : 'timelineMajorMarker'})[0]
        full_verses_entire = soup.find_all('dl', attrs={'class' : 'timelineMinor'})[0]
        full_verse = full_verses_entire.find_all('dt')

        total_verses_num = len(full_verse)
        for i in range(total_verses_num):
            contents = full_verse[i].contents
            verse_num = contents[0].text
            verse = contents[1].text
            connection.insert_verses()
            logging.info( 'crawling ' + full_book_name +  chapter)

        
    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")        
    
def ezoe_url_request(current_url):
    if current_url in visited_urls:
        return None

    print(f"Crawling : {current_url}")
    visited_urls.add(current_url)
    try:
        response = requests.get(current_url)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")
        return None

books_crawler(books_url_to_crawl)