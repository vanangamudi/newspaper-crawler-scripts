# -*- coding: utf-8 -*-
import urllib
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys



import logging
logging.basicConfig()
log = logging.getLogger('LOG')
log.setLevel(logging.DEBUG)


MAX_COUNT = 10000000
ROOT_URL = 'https://nakkheeran.in'
page = requests.get("https://nakkheeran.in")
soup = bs(page.content, 'html.parser')

visited_links = set()
with open('nakkheeran-visited-links.list', 'r') as f:
    visited_links = set(f.readlines())
    
links = [a.get('href') for a in soup.find_all('a', href=True)]

crawled_page_count = 0
index = 0

title_file = open('nakkheeran-title.list', 'a')

while len(links) != len(visited_links) or crawled_page_count < MAX_COUNT:

    current_link = links.pop(index)
    index += 1

    if current_link not in visited_links:
        if crawled_page_count > MAX_COUNT:
            break
        
        visited_links.add(current_link)

        try:
            page_name = urllib.parse.unquote(current_link)
            log.info('crawl_count: {} == processing: {}'.format(crawled_page_count, page_name))
            
            page = requests.get('{}{}'.format(ROOT_URL, current_link))
            soup = bs(page.content, 'html.parser')
            links.extend([a.get('href') for a in soup.find_all('a', href=True)])

            content = '\n\n'.join(i.text for i in soup.find(class_='post-content').find_all('p'))
            if not content:
                log.error('content extraction failed -- {}'.format(page_name))
                
            with open('nakkheeran/{}.txt'.format(page_name.split('/')[-1]), 'w') as f:
                f.write('{}\n------------------\n'.format(page_name))
                f.write(content)

            title = soup.find(class_='title page-title').text
            if not title:
                log.error('title extraction failed -- {}'.format(page_name))
            
            log.debug('title:= {}'.format(title))
            title_file.write('{}\n'.format(title))
                
            crawled_page_count += 1
        except KeyboardInterrupt:
            with open('nakkheeran-visited-links.list', 'w') as f:
                f.write('\n'.join(visited_links))
            exit(0)
        except:
            log.exception(current_link)


title_file.close()
