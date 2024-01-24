import requests
import random
import time
import logging
import re

from bs4 import BeautifulSoup
from databaseDao import MySQLBibleDatabase as DB

visited_urls = set()
ezoe_url = 'https://ezoe.work/bible/jw/'
books_url_to_crawl = 'https://ezoe.work/bible8/index.html'
chapters_url_to_crawl = 'https://ezoe.work/bible8/'

logging.basicConfig(filename='crawler.log', filemode='a', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO) 

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
            time.sleep(random.randint(2, 4))
            abbrevation = line.text
            url = line.attrs['href']
            next_url = chapters_url_to_crawl + url
            logging.info(f"crawling bible books %s", abbrevation)
            print(f"crawling bible books %s", abbrevation)
            if abbrevation == '约贰' or abbrevation == '约叁' or abbrevation == '犹':
                single_chapter_crawler(connection, next_url, abbrevation)
            else :
                chapters_crawler(connection, next_url, abbrevation)

    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def chapters_crawler(connection, current_url, abbrevation):
    try:
        logging.info(f"crawling bible chapter %s", abbrevation)
        print(f"crawling bible chapter {abbrevation}")

        # current_url = 'https://ezoe.work/bible8/1165.html'
        soup = ezoe_url_request(current_url)
        full_book_name = soup.find_all('h3')[0].text

        book_id = bDB.insert_book(connection, full_book_name, abbrevation, current_url)
        chapters = soup.find_all('a', attrs={'class':'page-navi'})

        logging.info("crawling chapters number is : %s ", len(chapters))
        print(f"crawling chapters number is : {len(chapters)} ")

        for line in chapters:
            chapter = line.text
            logging.info( 'crawling ' + full_book_name +  chapter)
            if not chapter.isdigit():
                logging.error( 'crawling wrong' + full_book_name +  chapter)
                continue

            url = line.attrs['href']
            full_chapter_url = chapters_url_to_crawl + url
            chapter_number = int(chapter)
            chapter_id = bDB.insert_chapater(connection, chapter_number, '', current_url, book_id)

            sleep_time = random.randint(4, 7)
            logging.info("currenty chapter is : %s ,  sleep time is %s", full_chapter_url, sleep_time)
            print("currenty chapter is : %s ,  sleep time is %s", full_chapter_url, sleep_time)
            verses_crawler(connection, full_chapter_url, chapter_number, full_book_name, chapter_id)
                                
    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def single_chapter_crawler(connection, current_url, abbrevation):
    try:
        logging.info(f"crawling specific bible chapter %s", abbrevation)
        print(f"crawling specific bible chapter {abbrevation}")

        # current_url = 'https://ezoe.work/bible8/1165.html'
        soup = ezoe_url_request(current_url)
        full_book_name = soup.find_all('h2')[0].text
        book_id = bDB.insert_book(connection, full_book_name, abbrevation, current_url)
        chapter_id = bDB.insert_chapater(connection, 1, '', current_url, book_id)
        sleep_time = random.randint(4, 7)
        logging.info("currenty chapter is : %s ,  sleep time is %s", current_url, sleep_time)
        print("currenty chapter is : %s ,  sleep time is %s", current_url, sleep_time)
        verses_crawler(connection, current_url, 1, full_book_name, chapter_id)
                                
    except Exception as e:
        logging.error(f"Error crawling {current_url}: {e}")

def verses_crawler(connection, current_url, chapter_number, full_book_name, chapter_id):
    try:
        logging.info( "Crawling verses :  %s ,  %s  ,  %s", full_book_name, chapter_number, current_url)
        print(f"Crawling verses :  {full_book_name} ,  {chapter_number}  ,  {current_url}")

        soup = ezoe_url_request(current_url)
        full_verses_entire = soup.find_all('dl', attrs={'class' : 'timelineMinor'})[0]
        full_verse = full_verses_entire.find_all('dt')

        total_verses_num = len(full_verse)
        logging.info("Total verses number is : %s", total_verses_num)

        for i in range(total_verses_num):
            contents = full_verse[i].contents
            verse_num = contents[0].text        ## TODO 2上

            if "下" in verse_num:
                continue
            if not verse_num.isdigit():
                logging.warning( 'crawling improper verser number  {full_book_name}, {chapter_number},  {verse_num}')
                verse_digits  = re.split(r'\D+', verse_num)
                verse_num = int("".join([str(x) for x in verse_digits]))
                pre_content_with_mark, pre_original_version_content = verse_handler(contents)
                suffix_content_with_mark, suffix_original_version_content = verse_handler(full_verse[i + 1].contents)

                content_with_mark = pre_content_with_mark + suffix_content_with_mark
                original_version_content = pre_original_version_content + suffix_original_version_content
            else:
                content_with_mark, original_version_content = verse_handler(contents)
            
            if original_version_content == '':
                logging.warning( "Crawling %s  %s verse is empty %s", full_book_name, chapter_number, current_url)

            bDB.insert_verses(connection, verse_num, original_version_content, content_with_mark, 
                      'chinese', '', current_url, chapter_number, chapter_id)

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

def verse_handler(contents):
    content_with_mark = contents[1].text
    ver_contents = contents[1].contents
    original_version_content = ''
    for v in ver_contents:
        v = str(v)
        if 'sup' not in v :
            original_version_content += v
    return content_with_mark, original_version_content

books_crawler(books_url_to_crawl)
