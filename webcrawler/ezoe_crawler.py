import requests
from bs4 import BeautifulSoup

visited_urls = set()

def books_crawler(url, max_depth=3):

    def books_abbrevation_crawl(current_url):
        try:
            soup = ezoe_request(current_url)
            books_name_abrevations = soup.find_all('a', attrs={'class':'page-navi'})
            # Extract information or perform actions here
            # Example: Print all the links on the page
            for line in books_name_abrevations:
                abbrevation = line.text
                url = line.attrs['href']
                next_url = ezoe_url + url
                chapaters_crawler(next_url, abbrevation)

        except Exception as e:
            print(f"Error crawling {current_url}: {e}")

    def chapaters_crawler(current_url, abbrevation):
        try:
            soup = ezoe_request(current_url)

            full_book_name = soup.find_all('p', attrs={'id':'chap1'})[0].text
            
            chapaters = soup.find_all('a', attrs={'class':'page-navi'})
            for line in chapaters:
                chapter = line.text
                if not chapter.isdigit():
                    chapter = full_book_name + ' ' + chapter 

                url = line.attrs['href']
                next_url = ezoe_url + url
                # crawl(next_url, depth + 1)
                    
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
    
    books_abbrevation_crawl(url)

def ezoe_request(current_url):
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
        print(f"Error crawling {current_url}: {e}")
        return None

# Example usage
ezoe_url = 'https://ezoe.work/bible/jw/'
books_url_to_crawl = 'https://ezoe.work/bible/jw/index.html'
chapaters_url_to_crawl = 'https://ezoe.work/bible/jw/hf_1_1.html'

books_crawler(books_url_to_crawl)
# chapaters_crawler(chapaters_url_to_crawl)