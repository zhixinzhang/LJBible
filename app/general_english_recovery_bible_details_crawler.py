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
ezoe_url = 'https://text.recoveryversion.bible/RcV.htm'
books_url_to_crawl = 'https://text.recoveryversion.bible/RcV.htm'
chapters_url_to_crawl = 'https://text.recoveryversion.bible/'

logging.basicConfig(filename='english_crawler.log', filemode='a', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO) 

bDB = DB.MySQLBibleDatabase(host="localhost", user="luke", password="123456", database="ljbible")
bDB.connect()
connection = bDB.connection


def books_crawler(url):
    books_abbrevation_crawl(connection, url)

def books_abbrevation_crawl(connection, current_url):
    try:
        soup = ezoe_url_request(current_url)
        all_books = soup.find_all("a", href=re.compile("_1.htm"))

        for line in all_books:
            time.sleep(random.randint(2, 4))
            eng_book_name = line.text
            url = line.attrs['href']
            next_url = chapters_url_to_crawl + url

            chapters_crawler(connection, next_url, eng_book_name)

    except Exception as e:
        logging.error("Error crawling books_abbrevation_crawl {} : {}".format(current_url, e))

def chapters_crawler(connection, current_url, eng_abbreviation_name):
    try:
       
        soup = ezoe_url_request(current_url)
        book = bDB.query_book_by_eng_abbreviation_name(connection, eng_abbreviation_name)
        all_chapters_count = book['chapter_count']

        cc = soup.find_all('div', attrs={'class':'chapter-links'})
        if len(cc) == 0 :
            logging.info("chapters_crawler Only one chapter bible {} chapters count is {} ".format(eng_abbreviation_name, all_chapters_count))
            print("chapters_crawler Only one chapter bible {} chapters count is {} ".format(eng_abbreviation_name, all_chapters_count))            
            chapter_num = 1
            sleep_time = random.randint(4, 8)
            time.sleep(sleep_time)
            verses_crawler(connection, current_url, book, chapter_num)
            return   

        all_chapters = soup.find_all('div', attrs={'class':'chapter-links'})[0].contents
        logging.info("Crawling bible {} chapters count is {} ".format(eng_abbreviation_name, all_chapters_count))
        print("Crawling bible {} chapters count is {} ".format(eng_abbreviation_name, all_chapters_count))

        for line in all_chapters:
            if line == '\n' or line == ' ' or line.attrs == None:
                continue
            if 'href' in line.attrs != None:
                url = line.attrs['href']
                chapter_num = line.text
                chapter_url = chapters_url_to_crawl + url
                logging.info("Crawling {}  :  {}".format(eng_abbreviation_name, chapter_num))

                sleep_time = 1
                logging.info("Current chapter is : %s ,  sleep time is %s", chapter_url, sleep_time)
                print('Current chapter is : {} , sleep time is {}'.format(chapter_url, sleep_time))
                verses_crawler(connection, chapter_url, book, chapter_num)
                                
    except Exception as e:
        logging.error("Error crawling chapters_crawler {} {}".format(current_url, e))

def verses_crawler(connection, current_url, book, chapter_num):
    try:
        full_book_name = book['book_name']

        soup = ezoe_url_request(current_url)    
        all_verses = soup.find_all('p', attrs={'class':'verse'})

        total_verses_num = len(all_verses)
        logging.info('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_num, total_verses_num, current_url))
        print('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_num, total_verses_num, current_url))

        verse_num = 1
        for verse_info in all_verses:
            print('Current verse :  {}'.format(verse_info.text))
            logging.info('Current verse :  {}'.format(verse_info.text))
            english_verse = ""
            original_verse = verse_info.text.replace("/", "")
            english_verse_contents = original_verse.split(" ")
            temp = re.sub(r'\d+', '', english_verse_contents[1])
            temp = temp.replace(":", " ")
            english_verse_contents[0] = ""
            english_verse_contents[1] = temp
            english_verse = " ".join(str(item) for item in english_verse_contents)
            english_verse = english_verse.strip()

            print('Current verse :  {}'.format(english_verse))
            logging.info('Current verse :  {}'.format(english_verse))
            if english_verse == '' or english_verse == None:
                print('Current book ?????????')
                logging.info('Current book ?????????')

            logging.info('Current book : {},   {} : {}, verses : {},  link : {}'.
                         format(full_book_name, chapter_num, verse_num, english_verse, current_url))
            print('Current book : {},   {} : {} , verses : {},  link : {}'.
                  format(full_book_name, chapter_num, verse_num, english_verse, current_url))
            
            verse = bDB.query_verse(connection, book['id'], chapter_num, verse_num)
            verse_content_id = bDB.insert_verse_content(connection, english_verse,
                                                         english_verse, Constants.english_recovery, current_url, verse['id'])
            print('Current verse_content_id : {}  verse :  {}'.format(verse_content_id, english_verse))

            verse_num = verse_num + 1
    except Exception as e:
        logging.error("Error crawling {} : {} verses_crawler  {} : {}".format(full_book_name, chapter_num, current_url, e))


def ezoe_url_request(current_url):
    # if current_url in visited_urls:
    #     return None

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
