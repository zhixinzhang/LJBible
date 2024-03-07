import requests
import random
import time
import logging
import re
import models.bible_constans as constans

import bs4
from bs4 import BeautifulSoup
from databaseDao import MySQLBibleDatabase as DB

visited_urls = set()
ezoe_url = 'https://ezoe.work/bible/jw/index.html'
books_url_to_crawl = 'https://ezoe.work/bible/jw/index.html'
chapters_url_to_crawl = 'https://ezoe.work/bible/jw/'

logging.basicConfig(filename='crawler.log', filemode='a', format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO) 

bDB = DB.MySQLBibleDatabase(host="localhost", user="luke", password="123456", database="ljbible")
bDB.connect()
connection = bDB.connection

bDB.drop_all_tables(connection)
bDB.initial_db('app/sql/ljbible.sql', connection)


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
            logging.info(f"Crawling bible books : %s", abbrevation)
            print(f"Crawling bible books : %s", abbrevation)
            chapters_crawler(connection, next_url, abbrevation)

    except Exception as e:
        logging.error("Error crawling books_abbrevation_crawl {} : {}".format(current_url, e))

def chapters_crawler(connection, current_url, abbrevation):
    try:
        logging.info('Crawling bible {}'.format(abbrevation))

        soup = ezoe_url_request(current_url)
        full_book_name = soup.find_all('p', attrs={'id':'chap1'})[0].text

        book_id = bDB.insert_book(connection, full_book_name, abbrevation, current_url)
        chapters = soup.find_all('a', attrs={'class':'page-navi'})

        logging.info("Crawling bible {} chapters count is {} ".format(full_book_name, len(chapters) - 2))
        print("Crawling bible {} chapters count is {} ".format(full_book_name, len(chapters) - 2))

        for line in chapters:
            chapter = line.text
            logging.info( 'crawling ' + full_book_name +  chapter)
            if not chapter.isdigit():       #TODO 鸟瞰，纲目
                logging.error("Crawling wrong {} : {}".format(full_book_name, chapter))
                continue

            url = line.attrs['href']
            full_chapter_url = chapters_url_to_crawl + url
            chapter_number = int(chapter)
            chapter_id = bDB.insert_chapater(connection, chapter_number, '', current_url, book_id)

            sleep_time = random.randint(4, 7)

            logging.info("Current chapter is : %s ,  sleep time is %s", full_chapter_url, sleep_time)
            print('Current chapter is : {} , sleep time is {}'.format(full_chapter_url, sleep_time))

            verses_crawler(connection, full_chapter_url, chapter_number, full_book_name, chapter_id)
                                
    except Exception as e:
        logging.error("Error crawling chapters_crawler {} {}".format(current_url, e))

def verses_crawler(connection, current_url, chapter_number, full_book_name, chapter_id):
    try:
        logging.info(f"Crawling verses :  %s ,  %s  ,  %s", full_book_name, chapter_number, current_url)
        print('Current book : {}, chapter : {} , link : {}'.format(full_book_name, chapter_number, current_url))

        # current_url = 'https://ezoe.work/bible/jw/hf_6_14.html'

        soup = ezoe_url_request(current_url)
        full_jy_original_verse = soup.find_all("a", href=re.compile("/jy/jx_"))
        full_xy_original_verse = soup.find_all("a", href=re.compile("/xy/jx_"))
        full_original_verse = full_jy_original_verse if len(full_xy_original_verse) == 0 else full_xy_original_verse

        total_verses_num = len(full_original_verse)
        logging.info('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_number, total_verses_num, current_url))
        print('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_number, total_verses_num, current_url))

        for i in range(total_verses_num):
            verse_num = full_original_verse[i].text
            original_verse = full_original_verse[i].nextSibling.replace('\u3000', '')
            
            single_verse_soup = full_original_verse[i].parent
            if len(single_verse_soup.attrs) != 0 and 'id' in single_verse_soup.attrs and single_verse_soup.attrs['id'] == 'ddt':
                logging.info(" Inserting Book {} : chapter : {}  verse without comments and beads {} : {}".format(full_book_name, chapter_number, verse_num, original_verse))
                verse_level = ''
                if not verse_num.isdigit():
                    all_verse_struc = re.split(r'(\d+)', verse_num)
                    verse_num = all_verse_struc[1]
                    verse_level = all_verse_struc[2]
                    print("Find a verse_level {} : {}".format(verse_num, verse_level))
                    logging.warn(" Fina a verver_level {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_number, verse_num, verse_level))
                
                verse_id = bDB.insert_verse(connection, verse_num, verse_level, False, False,chapter_number, chapter_id)
                
                # print(constans.chinese_recovery)
                verse_content_id = bDB.insert_verse_content(connection, original_verse, original_verse, 
                      constans.chinese_recovery, current_url, verse_id, verse_num)
                
                continue

            verse_with_beads_comments = single_verse_soup.parent
            sub_beads_comments = verse_with_beads_comments.contents
            for sub in sub_beads_comments:
                name = sub.name
                if name == 'dd':

                    comments, beads, v_with_mark = build_beads_comments(sub.contents)
                    print(" Inserting Book {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_number, verse_num, original_verse))
                    logging.info(" Inserting Book {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_number, verse_num, original_verse))
                    verse_level = ''
                    if not verse_num.isdigit():
                        all_verse_struc = re.split(r'(\d+)', verse_num)
                        verse_num = all_verse_struc[1]
                        verse_level = all_verse_struc[2]
                        print("Find a verse_level {} : {}".format(verse_num, verse_level))
                        logging.warn(" Fina a verver_level {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_number, verse_num, verse_level))

                    # verse_id = bDB.insert_verse(connection, verse_num, verse_level, False, False, original_verse, v_with_mark, 
                    #   'chinese', '', current_url, chapter_number, chapter_id)
                    

                    verse_id = bDB.insert_verse(connection, verse_num, verse_level, False, False, chapter_number, chapter_id)
                
                    # print(constans.chinese_recovery)
                    verse_content_id = bDB.insert_verse_content(connection, original_verse, v_with_mark, 
                        constans.chinese_recovery, current_url, verse_id, verse_num)
                    for k, v in comments.items():
                        if "词典" in k:
                            comment_num = 1         ##TODO https://ezoe.work/bible/jw/hf_11_9.html
                        else:
                            comment_num = k.replace('注', '')
                        comment_id = bDB.insert_comment(connection, comment_num, comment_num, v, current_url, verse_id)
                        print('comment - {} : {}'.format(k, v))

                    for k, v in beads.items():
                        bead_num = k.replace('串', '').split(' ')[0]
                        
                        mark = bead_num
                        original_beads = v.replace('\u3000', ' ')
                        bead_id = bDB.insert_bead(connection, bead_num, mark, original_beads, current_url, verse_id)
                        print('bead - {} : {}'.format(k, v))

    except Exception as e:
        logging.error("Error crawling {} : {} verses_crawler  {} : {}".format(full_book_name, chapter_number, current_url, e))


def build_beads_comments(contents):
    comment_dic = {}
    bead_dic = {}
    verse_with_mark =  None
    prev_comment_title = None
    prev_beat_title = None
    for content in contents:
        content_type = type(content)
        if content_type == bs4.element.Tag:
            att = content.attrs
            if len(att) == 0 and len(content.contents) != 0:
                cur_comments, cur_beads, cur_verse_with_mark = build_beads_comments(content.contents)
                bead_dic.update(cur_beads)
                comment_dic.update(cur_comments)
                verse_with_mark = cur_verse_with_mark if cur_verse_with_mark != None else verse_with_mark
                continue

            id = att['id']
            if id == 'AA00':
                verse_with_mark = content.text.split("\u3000")[1]
            if id == 'AA1':
                comment_title = content.text
                prev_comment_title = comment_title
                comment_dic.update({comment_title: None})
            if id == 'AA2':
                comment_content = content.text
                comment_dic.update({prev_comment_title: comment_content})
            if id == 'BB1':
                beat_title = content.text.replace('\u3000', '  ')
                prev_beat_title = beat_title
                bead_dic.update({beat_title: None})
            if id == 'BB2':
                beat_content = content.text
                bead_dic.update({prev_beat_title: beat_content})
    return comment_dic, bead_dic, verse_with_mark

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
