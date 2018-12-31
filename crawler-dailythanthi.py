# -*- coding: utf-8 -*-
import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys

from pprint import pprint, pformat
FORMAT_STRING = "%(levelname)-8s:%(name)-8s.%(funcName)-8s>> %(message)s"

import logging
logging.basicConfig(format=FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

MAX_COUNT = 1000000000000

ROOT_DIR = 'dailythanthi2'

LINKS_FILEPATH         = '{}/links.list'.format(ROOT_DIR)
VISITED_LINKS_FILEPATH = '{}/visited-links.list'.format(ROOT_DIR)

TITLE_LIST_FILEPATH    = '{}/title.list'        .format(ROOT_DIR)
ARTICLES_DIR           = '{}/articles'          .format(ROOT_DIR)
ABSTRACTS_DIR          = '{}/abstracts'         .format(ROOT_DIR)
COMMENTS_DIR           = '{}/comments'          .format(ROOT_DIR)

HTTP = 'http://'
HTTPS = 'https://'
ROOT_URL = 'www.dailythanthi.com'


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
    global name
    year, month = '0000', '00'
    m = re.search('(\d{4})\/(\d{2})/(\d+)\/(.*)', page_link)
    if m:
        log.debug(pformat(m))
        year, month, uid, name = m.groups()
        for d in SUBDIRS:
            mkdir('{}/{}/{}'.format(d, year, month))
            
    else:
        uid_ += 1
        uid = uid_
        
    return year, month, uid, name

def process_page(page_name, soup):
    global CRAWLED_PAGE_COUNT
    
    year, month, uid, name = extract_year_month(page_name, soup)
    log.info('year, month = {}, {}'.format(year, month))
    
    # remove all javascript and stylesheet code
    for script in soup(["script", "style"]): 
        script.extract()

    content = soup.find(id='ArticleDetailContent')
    if not content:
        log.error('content extraction failed')
        log.error('{}'.format(page_name))
    else:
        content = content.text
        with open('{}/{}/{}/{}.txt'.format(ARTICLES_DIR, year, month, name), 'w') as f:
            f.write('{}\n------------------\n'.format(page_name))
            f.write(content)

        # extract title
        title = soup.find('div', class_=['Article_Headline'])
        if not title:
            log.error('title extraction failed -- {}'.format(page_name))
        else:                    
            title_p = title.find('p')
            if title_p :
                title_p = title_p.extract()
                title_tamil, title_english = title_p.text.split('+ "||" +')

                log.info('title := {}'.format(title_tamil))
                title_file.write('ta:{}\n'.format(title_tamil.replace('\n', '').replace('\r', '')))
                title_file.write('en:{}\n'.format(title_english.replace('\n', '').replace('\r', '')))

            else:
                title_tamil = title.text
                title_file.write('ta:{}\n'.format(title_tamil.replace('\n', '').replace('\r', '')))

            title_file.write('\n\n')
            title_file.flush()

        #extract abstract
        abstract = soup.find(id='ArticleAbstract')
        if not abstract:
            log.error('abstract extraction failed')
            log.error('{}'.format(page_name))
        else:
            abstract = abstract.text
            with open('{}/{}/{}/{}.txt'.format(ABSTRACTS_DIR, year, month, name), 'w') as f:
                f.write('{}\n------------------\n'.format(page_name))
                f.write(abstract)


        """
        #extract comment
        iframes = soup.find('div', id= 'vuukle-comments')
        log.debug('IFRAMES: {}'.format(iframes))
        if not iframes:
            log.error('comment iframe extraction failed')
            log.error('== {}'.format(page_name))
        else:

            comments = iframe.find_all(class_='comment-content')
            if not comments:
                log.error('comment iframe extraction failed')
                log.error('== {}'.format(page_name))
            else:
                print(comments)
                comment = comments.text
                with open('{}/{}/{}/{}.txt'.format(COMMENTS_DIR, year, month, name), 'w') as f:
                    pass


        """
        CRAWLED_PAGE_COUNT += 1
        

if __name__ == '__main__':
    initialize_dir_structure()
    title_file = open(TITLE_LIST_FILEPATH, 'a')
    try:
        while len(LINKS) > 0 or CRAWLED_PAGE_COUNT < MAX_COUNT:
            print('\n')

            current_link = LINKS.pop(0).strip()
            if not url_check(current_link):
                current_link = HTTP + ROOT_URL + current_link

            if current_link not in VISITED_LINKS or len(current_link) < 30:
                if CRAWLED_PAGE_COUNT > MAX_COUNT:
                    break

                VISITED_LINKS.add(current_link)

                try:
                    page_name = urllib.parse.unquote(current_link)
                    log.info('crawl_count: {}'.format(CRAWLED_PAGE_COUNT))
                    log.info('processing: {}'.format(page_name))


                    # access current link content
                    page = requests.get('{}'.format(current_link))
                    soup = bs(page.content, 'html.parser')

                    # extract links
                    LINKS = extract_links(LINKS, VISITED_LINKS, soup)
                    log.info('LINKS count:= {}'.format(len(LINKS)))
                    log.debug(pformat(LINKS))

                    process_page(page_name, soup)

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
                log.info('already visited {}'.format(urllib.parse.unquote(current_link)))

    except:
        log.exception('###############')
        title_file.close()
        with open(VISITED_LINKS_FILEPATH, 'w') as f:
            f.write('\n'.join(VISITED_LINKS))

        with open(LINKS_FILEPATH, 'w') as f:
            f.write('\n'.join(LINKS))
