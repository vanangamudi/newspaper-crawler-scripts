# -*- coding: utf-8 -*-
import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys
import time
from pprint import pprint, pformat
FORMAT_STRING = "%(levelname)-8s:%(name)-8s.%(funcName)-8s>> %(message)s"

import logging
logging.basicConfig(format=FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

MAX_COUNT = 1000000000000

ROOT_DIR = 'manorama'

LINKS_FILEPATH         = '{}/links.list'.format(ROOT_DIR)
VISITED_LINKS_FILEPATH = '{}/visited-links.list'.format(ROOT_DIR)

TITLE_LIST_FILEPATH    = '{}/title.csv'        .format(ROOT_DIR)
ARTICLES_DIR           = '{}/articles'          .format(ROOT_DIR)
ABSTRACTS_DIR          = '{}/abstracts'         .format(ROOT_DIR)
COMMENTS_DIR           = '{}/comments'          .format(ROOT_DIR)

HTTP = 'http://'
HTTPS = 'https://'
ROOT_URL = 'www.manoramaonline.com'


CRAWLED_PAGE_COUNT = 0

def mkdir(path):
    if os.path.exists(path):
        return
    log.info('creating {}'.format(path))
    if os.makedirs(path):
        log.info('created {}'.format(path))



def url_check(a):
    log.debug(a)
    if (a.startswith(HTTP + ROOT_URL)
        or a.startswith(HTTPS + ROOT_URL)):
        log.debug('returning true')
        return True


def extract_links(LINKS, VISITED_LINKS, soup):
    links_ = [a.get('href')
              for a in soup.find_all('a', href=True)
              if url_check(a.get('href'))]
    
    LINKS.extend([i for i in links_ if i not in VISITED_LINKS])
    LINKS = list(set(LINKS))
    return LINKS
    

LINKS         = [HTTP + ROOT_URL, ]
VISITED_LINKS = set()
DIRS          = [ROOT_DIR, ARTICLES_DIR, COMMENTS_DIR, ABSTRACTS_DIR]
SUBDIRS       = [          ARTICLES_DIR, COMMENTS_DIR, ABSTRACTS_DIR]

def initialize_dir_structure():
    global LINKS
    global VISITED_LINKS
    
    log.info('creating subdirs')
    for d in DIRS:
        log.info('creating {}'.format(d))
        mkdir(d)

    VISITED_LINKS = set()
    try:
        with open(VISITED_LINKS_FILEPATH, 'r') as f:
            VISITED_LINKS = set(f.readlines())
    except FileNotFoundError:
        open(VISITED_LINKS_FILEPATH, 'w').close()

    try:
        with open(LINKS_FILEPATH, 'r') as f:
            LINKS.extend(list(set(f.readlines())))
    except FileNotFoundError:
        open(LINKS_FILEPATH, 'w').close()

        
uid_ = 0
name = '{}'.format(uid_)
def extract_year_month(page_link, soup):
    global uid_
    year, month = '0000', '00'
    # timestamp = soup.find(class_='ArticlePublish')

    timestamp = soup.find(class_='entryDate').contents[0]
    log.info(timestamp)
    # m = re.search(' (\w+) (\d{4}).*M', timestamp.text.strip())
    m = re.search('\w+ \d{2} (\w+) (\d{4}) \w+',timestamp.strip())
    if m:
        log.debug(pformat(m))
        month, year = m.groups()
        
    for d in SUBDIRS:
        mkdir('{}/{}/{}'.format(d, year, month))
            
    return year, month

def process_page(page_name, soup):
    global CRAWLED_PAGE_COUNT
    global uid_
    global title_file
    # remove all javascript and stylesheet code
    for script in soup(["script", "style"]): 
        script.extract()

    content = soup.find(id='storycontent')
    if not content:
        log.error('content extraction failed')
        log.error('{}'.format(page_name))
    else:
        print('=========== {}'.format(len(content)))        
        year, month = extract_year_month(page_name, soup)
        log.info('year, month = {}, {}'.format(year, month))

        m = re.search('{}\/([^\/]+)\/([^\/]+)\/[\d^\/]+([\w-]+).html'.format(ROOT_URL), page_name)
        if m:
            log.debug(pformat(m))
            type_of_news, class_label, page_title = m.groups()
        else:
            uid_ += 1
            class_label = '{}'.format(uid_)
            

        log.debug(content)
        paras = content.findAll('p')
        log.debug(pformat(paras))
        path_suffix = '{}/{}/{}.txt'.format(year, month, page_title)
        with open('{}/{}'.format(ARTICLES_DIR, path_suffix), 'w') as f:
            f.write('{}\n------------------\n'.format(page_name))
            f.write('\n'.join(p.text for p in paras))
            
        with open('{}/{}'.format(ABSTRACTS_DIR, path_suffix), 'w') as f:
            f.write('{}\n------------------\n'.format(page_name))
            f.write(paras[0].text)
            
        title = soup.find('h1', class_='articleheadingPage')
        log.info(title.text)
        title = title.text.replace("\n","").replace("\t","")
        breadcrumbs = soup.find(class_='breadcrumbs').findAll('a')
        breadcrumbs = ','.join([b.text.replace('\n', '').replace('\r', '')
                                for b in breadcrumbs])
        tags = soup.find(class_='storyTags').findAll('a')
        tags = ','.join([b.text.replace('\n', '').replace('\r', '')
                                for b in tags])
        log.info(breadcrumbs)
        log.info(tags)
        record = '{}|{}|{}|{}|{}|{}'.format(path_suffix, title, type_of_news,
                                      class_label, breadcrumbs,tags)
        title_file.write(record + '\n')
        CRAWLED_PAGE_COUNT += 1
        

if __name__ == '__main__':
    initialize_dir_structure()
    title_file = open(TITLE_LIST_FILEPATH, 'a')
    try:
        while len(LINKS) > 0 or CRAWLED_PAGE_COUNT < MAX_COUNT:
            print('####################')

            current_link = LINKS.pop(0).strip()
            # current_link ='https://www.manoramaonline.com/news/latest-news/2019/02/01/how-underworld-don-ravi-pujari-lives-in-african-countries.html'
            # current_link = "https://www.manoramaonline.com/news/latest-news/2019/02/02/rumours-on-sumalatha-to-contest-loksabha-polls-from-mandya.html"
            current_link = urllib.parse.unquote(current_link)
            if not url_check(current_link):
                current_link = HTTP + ROOT_URL + current_link

            if current_link not in VISITED_LINKS or len(current_link) < 30:
                if CRAWLED_PAGE_COUNT > MAX_COUNT:
                    break

                VISITED_LINKS.add(current_link)

                try:
                    page_name = current_link
                    log.info('crawl_count: {}'.format(CRAWLED_PAGE_COUNT))
                    log.info('processing: {}'.format(page_name))


                    # access current link content
                    page = requests.get('{}'.format(current_link))
                    soup = bs(page.content, 'html.parser')

                    # extract links
                    LINKS = extract_links(LINKS, VISITED_LINKS, soup)
                    LINKS = [l for l in LINKS if not re.search('videos|search', l)]
                    log.info('LINKS count:= {}'.format(len(LINKS)))
                    log.debug(pformat(LINKS))

                    process_page(page_name, soup)
                    if CRAWLED_PAGE_COUNT % 100: time.sleep(1)
                except KeyboardInterrupt:
                    with open(VISITED_LINKS_FILEPATH, 'w') as f:
                        f.write('\n'.join(VISITED_LINKS))

                    with open(LINKS_FILEPATH, 'w') as f:
                        f.write('\n'.join(LINKS))
                        
                    raise KeyboardInterrupt
                
                except:
                    log.exception(current_link)
                    with open(VISITED_LINKS_FILEPATH, 'w') as f:
                        f.write('\n'.join(VISITED_LINKS))
            else:
                log.info('already visited {}'.format(current_link))

    except:
        log.exception('###############')
        title_file.close()
        with open(VISITED_LINKS_FILEPATH, 'w') as f:
            f.write('\n'.join(VISITED_LINKS))

        with open(LINKS_FILEPATH, 'w') as f:
            f.write('\n'.join(LINKS))
