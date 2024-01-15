import requests
import random
import time
import logging

from bs4 import BeautifulSoup

from databaseDao import MySQLBibleDatabase as DB

ezoe_url = 'https://ezoe.work/bible/jw/'
books_url_to_crawl = 'https://ezoe.work/bible/jw/index.html'
chapaters_url_to_crawl = 'https://ezoe.work/bible/jw/hf_1_1.html'

visited_urls = set()
logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s', 
                    level=logging.INFO) 
  
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
            next_url = ezoe_url + url
            logging.info(f"crawling bible books %s", abbrevation)
            chapaters_crawler(connection, next_url, abbrevation)

    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def chapaters_crawler(connection, current_url, abbrevation):
    try:
        soup = ezoe_url_request(current_url)
        full_book_name = soup.find_all('p', attrs={'id':'chap1'})[0].text
        bDB.insert_book(connection, full_book_name, abbrevation, current_url)

        chapaters = soup.find_all('a', attrs={'class':'page-navi'})
        for line in chapaters:
            chapter = line.text
            if chapter == '鸟瞰' :
                logging.info( abbrevation + '鸟瞰')
                continue
            elif chapter == '纲目':
                logging.info( abbrevation + '纲目')
                continue
            if not chapter.isdigit():
                chapter = full_book_name + ' ' + chapter 

            url = line.attrs['href']
            full_chapater_url = ezoe_url + url
            
            verses_crawler(connection, full_chapater_url, chapter, full_book_name)
                                
    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def verses_crawler(connection, current_url, chapter, full_book_name):
    try:
        soup = ezoe_url_request(current_url)
        full_verses = soup.find_all('dl')
        verse_num = len(full_verses)
        for i in range(verse_num):
            verse_hidden = full_verses[i].find_all("dd")[0]
            h = verse_hidden.find_all('p')
            tag = h[0].attrs['id']

            if (tag == 'jian') :
                logging.info( "Crawling " + full_book_name + '简介')
                full_summary_verse = ''
                for element in h:
                    full_summary_verse = full_summary_verse + element.text + '\n'
                dd = 3
            elif (tag == 'AA00'):
                logging.info( "Crawling " + full_book_name + ' {i} ')
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
# chapaters_crawler(chapaters_url_to_crawl)