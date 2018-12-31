# -*- coding: utf-8 -*-
import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys

from pprint import pprint, pformat

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

MAX_COUNT = 1000000000000

ROOT_DIR = 'tamil.thehindu'

LINKS_FILEPATH         = '{}/links.list'.format(ROOT_DIR)
VISITED_LINKS_FILEPATH = '{}/visited-links.list'.format(ROOT_DIR)

TITLE_LIST_FILEPATH    = '{}/title.list'        .format(ROOT_DIR)
ARTICLES_DIR           = '{}/articles'          .format(ROOT_DIR)
ABSTRACTS_DIR          = '{}/abstracts'         .format(ROOT_DIR)
COMMENTS_DIR           = '{}/comments'          .format(ROOT_DIR)

ROOT_URL = 'https://tamil.thehindu.com'
page     = requests.get("https://tamil.thehindu.com")
soup     = bs(page.content, 'html.parser')


def mkdir(path):
    if os.path.exists(path):
        return
    log.info('creating {}'.format(path))
    if os.makedirs(path):
        log.info('created {}'.format(path))

DIRS = [ROOT_DIR, ARTICLES_DIR, COMMENTS_DIR, ABSTRACTS_DIR]
SUBDIRS = [ARTICLES_DIR, COMMENTS_DIR, ABSTRACTS_DIR]
log.info('creating subdirs')
for d in DIRS:
    log.info('creating {}'.format(d))
    mkdir(d)

visited_links = set()
with open(VISITED_LINKS_FILEPATH, 'r') as f:
    visited_links = set(f.readlines())
    
links = [ROOT_URL, ]

with open(LINKS_FILEPATH, 'r') as f:
    links.extend(list(set(f.readlines())))
    
crawled_page_count = 0
index = 0

title_file = open(TITLE_LIST_FILEPATH, 'a')

try:
    while len(links) > 0 or crawled_page_count < MAX_COUNT:

        current_link = links.pop(0)
        if not (current_link.startswith('http://tamil') or current_link.startswith('https://tamil')):
            current_link = ROOT_URL + current_link
            

        if current_link not in visited_links or len(current_link) < 30:
            if crawled_page_count > MAX_COUNT:
                break

            visited_links.add(current_link)

            try:
                page_name = urllib.parse.unquote(current_link)
                log.info('crawl_count: {}'.format(crawled_page_count))
                log.info('processing: {}'.format(page_name))


                # access current link content
                page = requests.get('{}'.format(current_link))
                soup = bs(page.content, 'html.parser')

                # extract links
                links_ = [a.get('href') for a in soup.find_all('a', href=True)]
                links.extend([i for i in links_ if i not in visited_links])
                links = list(set(links))
                log.info('links count:= {}'.format(len(links)))

                year, month = '0000', '00'
                timestamp = soup.find(class_='publisheddate')
                if timestamp:
                    timestamp = timestamp.text.split()
                    month, year = timestamp[3], timestamp[4]
                    for d in SUBDIRS:
                        mkdir('{}/{}/{}'.format(d, year, month))
                
                print(year, month)
                # remove all javascript and stylesheet code
                for script in soup(["script", "style"]): 
                    script.extract()

                content = soup.find(class_=['bodycontent'])
                if not content:
                    log.error('content extraction failed')
                    log.error('{}'.format(page_name))
                else:
                    m = re.search('(article.*.ece)', page_name)
                    if m:
                        name = m.group(1)
                    
                    # extract title
                    title = soup.find('h1', class_=['title', 'mbot10'])
                    if not title:
                        log.error('title extraction failed -- {}'.format(page_name))
                    else:                    
                        title_p = title.text
                        log.info('title:= {}'.format(title_p))
                        title_file.write(title_p)

                        title_file.write('\n')
                        title_file.flush()
                        

                    paragraphs = content.find_all('p')
                    
                    content = '\n'.join([i.text for i in paragraphs[1:]])
                    with open('{}/{}/{}/{}.txt'.format(ARTICLES_DIR, year, month, name), 'w') as f:
                        f.write('{}\n------------------\n'.format(page_name))
                        f.write(content)


                    abstract = paragraphs[0].text
                    with open('{}/{}/{}/{}.txt'.format(ABSTRACTS_DIR, year, month, name), 'w') as f:
                        f.write('{}\n------------------\n'.format(page_name))
                        f.write(abstract)

                    crawled_page_count += 1
                    
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


            except KeyboardInterrupt:
                with open(VISITED_LINKS_FILEPATH, 'w') as f:
                    f.write('\n'.join(visited_links))
                    
                with open(LINKS_FILEPATH, 'w') as f:
                    f.write('\n'.join(links))
                exit(0)
            except:
                log.exception(current_link)
                with open(VISITED_LINKS_FILEPATH, 'w') as f:
                    f.write('\n'.join(visited_links))
        else:
            log.info('already visited {}'.format(urllib.parse.unquote(current_link)))

except:
    title_file.close()
    with open(VISITED_LINKS_FILEPATH, 'w') as f:
        f.write('\n'.join(visited_links))
    
    with open(LINKS_FILEPATH, 'w') as f:
        f.write('\n'.join(links))
