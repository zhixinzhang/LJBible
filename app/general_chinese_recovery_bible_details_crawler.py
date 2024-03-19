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
        new_or_old = 'New'
        for line in books_name_abrevations:
            time.sleep(random.randint(2, 4))
            abbrevation_cn = line.text
            url = line.attrs['href']
            next_url = chapters_url_to_crawl + url

            if abbrevation_cn == "玛":
                new_or_old = "Old"

            full_book_info = Constants.Bible_Books_Info[abbrevation_cn]
            book_name_cn = full_book_info[0]
            abbrevation_eng = full_book_info[1]
            book_name_eng = full_book_info[2]
            book_type = full_book_info[3]

            chapter_soup = ezoe_url_request(next_url)
            chapters = chapter_soup.find_all('a', attrs={'class':'page-navi'})
            chapter_num = len(chapters) - 2

            # def insert_book(self, connection, abbrevation_cn, book_name_cn, 
            #         abbrevation_eng, book_name_eng, chapter_num, new_or_old, book_type, author):
            book_id = bDB.insert_book(connection, abbrevation_cn, book_name_cn, abbrevation_eng, book_name_eng, chapter_num, 
                                      new_or_old, book_type, '')
            
            # def insert_book_content(self, connection, book_name_cn, version, descriptions, crawler_link, book_id):

            book_content_id = bDB.insert_book_content(connection, book_name_cn, Constants.Book_Version_Recovery, '', next_url, book_id)

            logging.info("Crawling bible books : {} - {}  {} : {}".format(book_name_cn, book_name_eng, new_or_old, book_type))
            print("Crawling bible books : {} - {}  {} : {}".format(book_name_cn, book_name_eng, new_or_old, book_type))

            chapters_crawler(connection, next_url, book_name_cn, abbrevation_cn, abbrevation_eng, book_id, book_content_id, chapters)

    except Exception as e:
        logging.error("Error crawling books_abbrevation_crawl {} : {}".format(current_url, e))

def chapters_crawler(connection, current_url, full_book_name, abbrevation_cn, abbrevation_eng, book_id, book_content_id, chapters):
    try:
        logging.info('Crawling bible {}'.format(abbrevation_cn))

        for line in chapters:
            chapter = line.text
            logging.info( 'crawling ' + full_book_name + "  Chapter : " + chapter)
            if not chapter.isdigit():       #TODO 鸟瞰，纲目
                logging.error("Crawling wrong {} : {}".format(full_book_name, chapter))
                continue

            url = line.attrs['href']
            full_chapter_url = chapters_url_to_crawl + url
            chapter_num = int(chapter)

            chapter_id = bDB.insert_chapater(connection, chapter_num, '', current_url, book_content_id)  # book_id -> book_content_id

            sleep_time = 1
            time.sleep(1)

            logging.info("Current chapter is : %s ,  sleep time is %s", full_chapter_url, sleep_time)
            print('Current chapter is : {} , sleep time is {}'.format(full_chapter_url, sleep_time))

            verses_crawler(connection, full_chapter_url, chapter_num, full_book_name, abbrevation_cn, abbrevation_eng, chapter_id)
                                
    except Exception as e:
        logging.error("Error crawling chapters_crawler {} {}".format(current_url, e))

def verses_crawler(connection, current_url, chapter_num, full_book_name, abbrevation_cn, abbrevation_eng, chapter_id):
    try:
        logging.info(f"Crawling verses :  %s ,  %s  ,  %s", full_book_name, chapter_num, current_url)
        print('Current book : {}, chapter : {} , link : {}'.format(full_book_name, chapter_num, current_url))

        soup = ezoe_url_request(current_url)
        full_jy_original_verse = soup.find_all("a", href=re.compile("/jy/jx_"))
        full_xy_original_verse = soup.find_all("a", href=re.compile("/xy/jx_"))
        full_original_verse = full_jy_original_verse if len(full_xy_original_verse) == 0 else full_xy_original_verse

        total_verses_num = len(full_original_verse)
        logging.info('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_num, total_verses_num, current_url))
        print('Current book : {}, chapter : {} , total verses number : {},  link : {}'.format(full_book_name, chapter_num, total_verses_num, current_url))

        for i in range(total_verses_num):
            verse_num = full_original_verse[i].text
            original_verse = full_original_verse[i].nextSibling.replace('\u3000', '')
            original_verse = original_verse.strip()

            single_verse_soup = full_original_verse[i].parent
            if len(single_verse_soup.attrs) != 0 and 'id' in single_verse_soup.attrs and 'ddt' in single_verse_soup.attrs['id'] :
                logging.info(" Inserting Book {} : chapter : {}  verse without comments and beads {} : {}".format(full_book_name, chapter_num, verse_num, original_verse))
                verse_level = ''
                if not verse_num.isdigit():
                    all_verse_struc = re.split(r'(\d+)', verse_num)
                    verse_num = all_verse_struc[1]
                    verse_level = all_verse_struc[2]
                    print("Find a verse_level {} : {}".format(verse_num, verse_level))
                    logging.warn(" Fina a verver_level {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_num, verse_num, verse_level))
                
                verse_id = bDB.insert_verse(connection, verse_num, verse_level, False, False, chapter_num, chapter_id)
                verse_content_id = bDB.insert_verse_content(connection, original_verse, original_verse, Constants.chinese_recovery, current_url, verse_id)
                continue

            verse_with_beads_comments = single_verse_soup.parent
            sub_beads_comments = verse_with_beads_comments.contents
            dd_exist = False
            for sub in sub_beads_comments:
                name = sub.name
                if name == 'dd':
                    dd_exist = True
                    comments, beads, v_with_mark = build_beads_comments(sub.contents)
                    print(" Inserting Book {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_num, verse_num, original_verse))
                    logging.info(" Inserting Book {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_num, verse_num, original_verse))
                    verse_level = ''
                    if not verse_num.isdigit():
                        all_verse_struc = re.split(r'(\d+)', verse_num)
                        verse_num = all_verse_struc[1]
                        verse_level = all_verse_struc[2]
                        print("Find a verse_level {} : {}".format(verse_num, verse_level))
                        logging.warn(" Fina a verver_level {} : chapter : {}  verse {} : {}".format(full_book_name, chapter_num, verse_num, verse_level))
                    
                    verse_id = bDB.insert_verse(connection, verse_num, verse_level, False, False, chapter_num, chapter_id)
                    verse_content_id = bDB.insert_verse_content(connection, original_verse, v_with_mark, Constants.chinese_recovery, current_url, verse_id)

                    for k, v in comments.items():
                        if "词典" in k:
                            comment_num = 1         ##TODO https://ezoe.work/bible/jw/hf_11_9.html
                        else:
                            comment_num = k.replace('注', '')
                        v = v.strip()
                        comment_id = bDB.insert_comment(connection, comment_num, comment_num, v, current_url, verse_content_id) # verse_id -> verse_content_id
                        print('comment - {} : {}'.format(k, v))

                    for k, v in beads.items():
                        if len(v) == 0:
                            print("Current beads is empty : {}".format(original_verse))
                            continue
                        bead_num = k.replace('串', '').split(' ')[0]
                        bead_range = k.replace('串', '').split('  ')[1]
                        
                        mark = bead_num
                        original_beads = v[0].replace('\u3000', ' ')
                        bead_id = bDB.insert_bead(connection, bead_num, bead_range, mark, original_beads, current_url, verse_content_id)

                        cc = len(v)
                        for i in range(1, len(v)):
                            cur_bead = v[i]
                            cur_bead_content = cur_bead.split("\u3000")
                            bead_verse_position = cur_bead_content[0]
                            bead_verse_info = cur_bead_content[1]
                            all_verse_struc = re.split(r'(\d+)', bead_verse_position)
                            located_cn_abbrevation = all_verse_struc[0]

                            loacted_book_info = Constants.Bible_Books_Info[located_cn_abbrevation]
                            located_eng_abbrevation = loacted_book_info[1]

                            located_chapter_num = all_verse_struc[1]
                            located_verse_num = all_verse_struc[3]
                            content = bead_verse_info
                            original_content = cur_bead.replace("\u3000", "   ")

                            bDB.insert_bead_contents(connection, 
                                                     abbrevation_cn, abbrevation_eng, located_cn_abbrevation, located_eng_abbrevation, 
                                                     chapter_num, verse_num, located_chapter_num, located_verse_num, content, original_content, bead_id, 
                                verse_content_id, current_url)
                        
                        print('bead - {} : {}'.format(k, v))
                    v_with_mark = ''
                    beads = None
                    comments = None
            
            if not dd_exist :
                verse_id = bDB.insert_verse(connection, verse_num, verse_level, False, False, chapter_num, chapter_id)
                verse_content_id = bDB.insert_verse_content(connection, original_verse, v_with_mark, Constants.chinese_recovery, current_url, verse_id)

    except Exception as e:
        logging.error("Error crawling {} : {} verses_crawler  {} : {}".format(full_book_name, chapter_num, current_url, e))


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
                # CC : https://ezoe.work/bible/jw/hf_23_11.html  𣎴：dǔn　筏树后的根株。
                if prev_comment_title is None:
                    continue
                comment_dic.update({prev_comment_title: comment_content})
            if id == 'BB1':
                beat_title = content.text.replace('\u3000', '  ')
                prev_beat_title = beat_title
                bead_dic.update({beat_title: None})
            if id == 'BB2':
                beat_contents = content.text.strip()
                beat_content_list = [beat_contents]
                contents = content.contents
                for c in contents:
                    c_type = type(c)
                    if c_type != bs4.element.Tag:
                        beat_content_list.append(c.strip())
                        
                bead_dic.update({prev_beat_title: beat_content_list})

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
