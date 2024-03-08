import requests
import random
import time
import logging
import re
import models.bible_constans as Constants

import bs4
from bs4 import BeautifulSoup
from databaseDao import MySQLBibleDatabase as DB

visited_urls = set()
ezoe_url = 'https://ezoe.work/bible/jw/index.html'
books_url_to_crawl = 'https://ezoe.work/Bible00/Bible.html'
chapters_url_to_crawl = 'https://ezoe.work/Bible00/'

logging.basicConfig(filename='english_crawler.log', filemode='a', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO) 

bDB = DB.MySQLBibleDatabase(host="localhost", user="luke", password="123456", database="ljbible")
bDB.connect()
connection = bDB.connection


def books_crawler(url):
    books_abbrevation_crawl(connection, url)

def books_abbrevation_crawl(connection, current_url):
    try:
        soup = ezoe_url_request(current_url)
        all_books = soup.find_all("a", href=re.compile("Chapters/Chapters_"))

        for line in all_books:
            time.sleep(random.randint(2, 4))
            book_name = line.text.split(" ")[1]
            url = line.attrs['href']
            next_url = chapters_url_to_crawl + url
            logging.info(f"Crawling bible books : %s", book_name)
            print(f"Crawling bible books : %s", book_name)
            chapters_crawler(connection, next_url, book_name)

    except Exception as e:
        logging.error("Error crawling books_abbrevation_crawl {} : {}".format(current_url, e))

def chapters_crawler(connection, current_url, book_name):
    try:
        logging.info('chapters_crawler Crawling bible {}'.format(book_name))
        print('chapters_crawler Crawling bible {}'.format(book_name))

        soup = ezoe_url_request(current_url)
        all_chapters = soup.find_all("a", href=re.compile("../Show/"))
        book = bDB.query_book_by_name(connection, book_name)

        logging.info("Crawling bible {} chapters count is {} ".format(book_name, len(all_chapters) - 2))
        print("Crawling bible {} chapters count is {} ".format(book_name, len(all_chapters) - 2))

        chapter_num = 0
        for line in all_chapters:
            chapter_num += 1
            logging.info("Crawling {}  :  {}".format(book_name, chapter_num))

            url = line.attrs['href'].replace("../", "")
            full_chapter_url = chapters_url_to_crawl + url

            sleep_time = random.randint(4, 8)

            logging.info("Current chapter is : %s ,  sleep time is %s", full_chapter_url, sleep_time)
            print('Current chapter is : {} , sleep time is {}'.format(full_chapter_url, sleep_time))

            verses_crawler(connection, full_chapter_url, book, chapter_num)
                                
    except Exception as e:
        logging.error("Error crawling chapters_crawler {} {}".format(current_url, e))

def verses_crawler(connection, current_url, book, chapter_num):
    try:
        full_book_name = book['book_name']
        logging.info("Crawling verses Current book : {}, chapter : {} , link : {}".format(full_book_name, chapter_num, current_url))
        print("Crawling verses Current book : {}, chapter : {} , link : {}".format(full_book_name,  chapter_num,current_url))

        # current_url = "https://ezoe.work/Bible00/Show/Pas004.html"
        # current_url = "https://ezoe.work/Bible00/Show/Pas001.html"
        soup = ezoe_url_request(current_url)
        all_verses = soup.find_all('li', attrs={'style':'white-space: normal'})

        total_verses_num = len(all_verses)
        logging.info('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_num, total_verses_num, current_url))
        print('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_num, total_verses_num, current_url))

        for content in all_verses:
            verse = content.text.strip()
            if full_book_name == "诗篇" and ":0" in verse:
                continue
            if "\u3000" in verse :
                verse_chapter_num = verse.split('\u3000')[0]
                verse_num = verse_chapter_num.split(":")[1]
                english_verse_content = verse.split('\u3000')[1].replace("\n", "")

            else :
                verse_chapter_num = verse.split(' ')[0]
                verse_num = verse_chapter_num.split(":")[1]
                english_verse_content = verse.replace(verse_chapter_num, '').replace('(', '').replace('\n', '')

            logging.info('Current book : {},   {} : {}, verses : {},  link : {}'.
                         format(full_book_name, chapter_num, verse_num, english_verse_content, current_url))
            print('Current book : {},   {} : {} , verses : {},  link : {}'.
                  format(full_book_name, chapter_num, verse_num, english_verse_content, current_url))
            
            verse = bDB.query_verse(connection, book['id'], chapter_num, verse_num)
            verse_content_id = bDB.insert_verse_content(connection, english_verse_content, english_verse_content, Constants.english_recovery, current_url, verse['id'])

    except Exception as e:
        logging.error("Error crawling {} : {} verses_crawler  {} : {}".format(full_book_name, chapter_num, current_url, e))


def ezoe_url_request(current_url):
    if current_url in visited_urls:
        return None

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
