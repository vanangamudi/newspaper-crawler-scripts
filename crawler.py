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

import config
import logging
logging.basicConfig(format=config.CONFIG.FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(config.CONFIG.LOGLEVEL)


HTTP  = 'http://'
HTTPS = 'https://'

def mkdir(path):
    if os.path.exists(path):
        return
    log.info('creating {}'.format(path))
    if os.makedirs(path):
        log.info('created {}'.format(path))
        

PREFIX = '{}/{}'.format(os.path.dirname(__file__), 'data')

class Crawler(object):


    def __init__(self, root_url, root_dir='', prefix=PREFIX):

        print(prefix)
        self.ROOT_URL = root_url
        if root_dir:
            self.ROOT_DIR = root_dir
        else:
            self.ROOT_DIR = ROOT_URL.replace(HTTPS).replace(HTTP).split('/')[0]
        
        self.LINKS_FILEPATH         = '{}/{}/links.list'         .format(prefix, self.ROOT_DIR)
        self.VISITED_LINKS_FILEPATH = '{}/{}/visited-links.list' .format(prefix, self.ROOT_DIR)
        
        self.TITLE_LIST_FILEPATH    = '{}/{}/title.csv'          .format(prefix, self.ROOT_DIR)
        self.ARTICLES_DIR           = '{}/{}/articles'           .format(prefix, self.ROOT_DIR)
        self.ABSTRACTS_DIR          = '{}/{}/abstracts'          .format(prefix, self.ROOT_DIR)

        self.LINKS         = [
            HTTP + self.ROOT_URL,
            'viduthalai.in/home/world-news/103-world-general/176740-2019-02-14-10-09-11.html',
        ]
        
        self.VISITED_LINKS = set()
        self.DIRS          = [self.ROOT_DIR,
                              self.ARTICLES_DIR,
                              self.ABSTRACTS_DIR]
        
        self.SUBDIRS       = self.DIRS[1:]
    
        self.CRAWLED_PAGE_COUNT = 0
        self.MAX_COUNT = 1000000000000
        
    def initialize_dir_structure(self):
        log.info('creating subdirs')
        for d in self.DIRS:
            log.info('creating {}'.format(d))
            mkdir(d)

        self.VISITED_LINKS = set()
        try:
            with open(self.VISITED_LINKS_FILEPATH, 'r') as f:
                self.VISITED_LINKS = set(f.readlines())
        except FileNotFoundError:
            open(self.VISITED_LINKS_FILEPATH, 'w').close()

        try:
            with open(self.LINKS_FILEPATH, 'r') as f:
                self.LINKS.extend(list(set(f.readlines())))
        except FileNotFoundError:
            open(self.LINKS_FILEPATH, 'w').close()

    def url_check(self, a):
        log.debug(a)
        if (a.startswith(HTTP + self.ROOT_URL)
            or a.startswith(HTTPS + self.ROOT_URL)):
            log.debug('returning true')
            return True

    def extract_links(self, soup, LINKS, VISITED_LINKS):
        links_ = [a.get('href')
                  for a in soup.find_all('a', href=True)]

        LINKS.extend([i for i in links_ if i not in VISITED_LINKS])
        LINKS = list(set(LINKS))
        return LINKS

    def extract_year_month(self):
        raise NotImplemented

    def process_page(self):
        raise NotImplemented

    def write_state(self):
        with open(self.VISITED_LINKS_FILEPATH, 'w') as f:
            f.write('\n'.join(self.VISITED_LINKS))
            
        with open(self.LINKS_FILEPATH, 'w') as f:
            f.write('\n'.join(self.LINKS))

        return True

    def url_filter(self, url):
        return True
    
    def crawl(self):
        title_file = open(self.TITLE_LIST_FILEPATH, 'a')
        try:
            while len(self.LINKS) > 0 and self.CRAWLED_PAGE_COUNT < self.MAX_COUNT:

                current_link = self.LINKS.pop(0).strip()
                current_link = urllib.parse.unquote(current_link)
                print('=========')
                log.info('processing: {}'.format(current_link))
                print('processing: {}'.format(current_link))

                if not self.url_check(current_link):
                    current_link = HTTP + self.ROOT_URL + current_link

                if current_link not in self.VISITED_LINKS:
                    if self.CRAWLED_PAGE_COUNT > self.MAX_COUNT:
                        break

                    self.VISITED_LINKS.add(current_link)

                    try:
                        log.info('crawl_count: {}'.format(self.CRAWLED_PAGE_COUNT))
                        # access current link content
                        page = requests.get('{}'.format(current_link))
                        soup = bs(page.content, 'html.parser')

                        # extract links
                        self.LINKS = self.extract_links(soup, self.LINKS, self.VISITED_LINKS)
                        self.LINKS = [l for l in self.LINKS if self.url_filter(l)]
                        
                        log.info('LINKS count:= {}'.format(len(self.LINKS)))
                        print(' Number to links:=')
                        print('  To be visited: {}'.format(len(self.LINKS)))
                        print('  Visited Links: {}'.format(len(self.VISITED_LINKS)))
                        print('  Crawled Count: {}'.format(self.CRAWLED_PAGE_COUNT))                        
                        log.debug(pformat(self.LINKS))

                        path_suffix, metadata_record, contents = self.process_page(current_link, soup)
                        print('  path: {}'.format(path_suffix))
                        for dir_, content in contents.items():
                            with open('{}/{}'.format(dir_, path_suffix), 'w') as f:
                                f.write('{}'.format(current_link))
                                f.write('\n------------------\n')
                                f.write(content)
                                
                        title_file.write(metadata_record + '\n')
                        self.CRAWLED_PAGE_COUNT += 1
                        
                        if self.CRAWLED_PAGE_COUNT % 100:
                            time.sleep(1)
                        
                    except KeyboardInterrupt:
                        with open(self.VISITED_LINKS_FILEPATH, 'w') as f:
                            f.write('\n'.join(self.VISITED_LINKS))

                        with open(self.LINKS_FILEPATH, 'w') as f:
                            f.write('\n'.join(self.LINKS))

                        raise KeyboardInterrupt

                    except:
                        log.exception(current_link)
                        with open(self.VISITED_LINKS_FILEPATH, 'w') as f:
                            f.write('\n'.join(self.VISITED_LINKS))
                else:
                    log.info('already visited {}'.format(current_link))
                    print('already visited')

        except:
            log.exception('###############')
            title_file.close()
            with open(self.VISITED_LINKS_FILEPATH, 'w') as f:
                f.write('\n'.join(self.VISITED_LINKS))

            with open(self.LINKS_FILEPATH, 'w') as f:
                f.write('\n'.join(self.LINKS))
