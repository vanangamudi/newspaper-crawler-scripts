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

def verbose(*args, **kwargs):
    if config.CONFIG.VERBOSE:
        print(*args, **kwargs)


def remove_everything_after_hashquestion(url):
    url = url.split('?')[0]
    url = url.split('#')[0]
    return url
    
class Crawler(object):


    def __init__(self, root_url, root_dir='', prefix=PREFIX):

        verbose(prefix)
        
        self.ROOT_URL = root_url
        if root_dir:
            root_dir = '/'.join(root_dir.split('/')[-2:])
            root_dir = root_dir.replace('crawler-', '').replace('.py', '')
            print('root directory for storing data is {}'.format(root_dir))
        
            self.ROOT_DIR = root_dir
        else:
            self.ROOT_DIR = self.ROOT_URL.replace(HTTPS,'').replace(HTTP, '').split('/')[0]
        
        self.LINKS_FILEPATH         = '{}/{}/links.list'         .format(prefix, self.ROOT_DIR)
        self.VISITED_LINKS_FILEPATH = '{}/{}/visited-links.list' .format(prefix, self.ROOT_DIR)
        
        self.TITLE_LIST_FILEPATH    = '{}/{}/title.csv'          .format(prefix, self.ROOT_DIR)
        self.ARTICLES_DIR           = '{}/{}/articles'           .format(prefix, self.ROOT_DIR)
        self.ABSTRACTS_DIR          = '{}/{}/abstracts'          .format(prefix, self.ROOT_DIR)

        self.LINKS         = [
            HTTP + self.ROOT_URL,
        ]
        
        self.VISITED_LINKS = set()
        self.DIRS          = [self.ROOT_DIR,
                              self.ARTICLES_DIR,
                              self.ABSTRACTS_DIR]
        
        self.SUBDIRS       = self.DIRS[1:]
    
        self.CRAWLED_PAGE_COUNT = 0
        self.MAX_COUNT = 10000000000000000000000
        
    def initialize_dir_structure(self):
        log.info('creating subdirs')
        for d in self.DIRS:
            log.info('creating {}'.format(d))
            mkdir(d)

        self.VISITED_LINKS = set()
        try:
            with open(self.VISITED_LINKS_FILEPATH, 'r') as f:
                self.VISITED_LINKS = set(
                    remove_everything_after_hashquestion(i) for i in f.readlines()
                )
                
        except FileNotFoundError:
            open(self.VISITED_LINKS_FILEPATH, 'w').close()

        try:
            with open(self.LINKS_FILEPATH, 'r') as f:
                links = list(set(f.readlines()))
                for i in links:
                    i = remove_everything_after_hashquestion(i)
                    if  i not in self.VISITED_LINKS and self.url_filter(i):
                        self.LINKS.append(i)
                
        except FileNotFoundError:
            open(self.LINKS_FILEPATH, 'w').close()

    def url_check(self, a):
        log.debug(a)
        if (a.startswith(HTTP + self.ROOT_URL)
            or a.startswith(HTTPS + self.ROOT_URL)):
            log.debug('returning true')
            return True

    def extract_links(self, soup):
        links_ = [a.get('href')
                  for a in soup.find_all('a', href=True)]

        for i in links_:
            i = remove_everything_after_hashquestion(i)
            if i not in self.VISITED_LINKS and self.url_filter(i):
                self.LINKS.append(i)
            
        return self.LINKS

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

    def elapsed_period(self):
        end = time.time()
        hours, rem = divmod(end-self.start_time, 3600)
        minutes, seconds = divmod(rem, 60)
        return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)
        
    def crawl(self):
        title_file = open(self.TITLE_LIST_FILEPATH, 'a')
        self.start_time = time.time()
        try:
            while len(self.LINKS) > 0 and self.CRAWLED_PAGE_COUNT < self.MAX_COUNT:

                current_link = self.LINKS.pop(0).strip()
                current_link = urllib.parse.unquote(current_link)
                verbose('=========')
                print('  Elapsed: {} :  Crawled Count: {}'.format(self.elapsed_period(),
                                                                  self.CRAWLED_PAGE_COUNT),
                      end='\r' if config.CONFIG.VERBOSE else '\n')

                log.info('processing: {}'.format(current_link))
                verbose('processing: {}'.format(current_link))

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
                        self.extract_links(soup)
                        
                        log.info('LINKS count:= {}'.format(len(self.LINKS)))
                        verbose(' Number to links:=')
                        verbose('  To be visited: {}'.format(len(self.LINKS)))
                        verbose('  Visited Links: {}'.format(len(self.VISITED_LINKS)))
                        verbose('  Crawled Count: {}'.format(self.CRAWLED_PAGE_COUNT))                        
                        log.debug(pformat(self.LINKS))

                        path_suffix, metadata_record, contents = self.process_page(current_link, soup)
                        verbose('  path: {}'.format(path_suffix))
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
                        raise KeyboardInterrupt

                    except:
                        log.exception(current_link)
                        self.write_state()
                else:
                    log.info('already visited {}'.format(current_link))
                    verbose('already visited')

        except:
            log.exception('###############')
            title_file.close()
            self.write_state()


import threading
class MultiThreadedCrawler(Crawler):

    def __init__(self, root_url, root_dir='', prefix=PREFIX, num_threads=12):
        super().__init__(root_url, root_dir, prefix)
        self.NUM_THREADS = num_threads


    def crawl(self):
        self.title_file = open(self.TITLE_LIST_FILEPATH, 'a')

        threads = []
        self.lock = threading.Lock()
        for i in range(self.NUM_THREADS):
            verbose('starting thread {}'.format(i))
            t = threading.Thread(target=self.crawl_)
            threads.append(t)
            t.start()

        for t in threads:
            verbose('joining thread {}'.format(t))
            t.join()
            

    def crawl_(self):
        break_loop = False
        self.start_time = time.time()
        try:
            while not break_loop:
                current_link = self.LINKS.pop(0).strip()
                current_link = urllib.parse.unquote(current_link)
                verbose('=========')
                print('  Elapsed: {} :  Crawled Count: {}'.format(self.elapsed_period(),
                                                                  self.CRAWLED_PAGE_COUNT),
                      end='\r')
                
                log.info('processing: {}'.format(current_link))
                verbose('processing: {}'.format(current_link))

                if not self.url_check(current_link):
                    current_link = HTTP + self.ROOT_URL + current_link

                if current_link not in self.VISITED_LINKS:
                    if self.CRAWLED_PAGE_COUNT > self.MAX_COUNT:
                        break
                    
                    self.lock.acquire()
                    self.VISITED_LINKS.add(current_link)
                    self.lock.release()
                    
                    try:
                        log.info('crawl_count: {}'.format(self.CRAWLED_PAGE_COUNT))
                        # access current link content
                        page = requests.get('{}'.format(current_link))
                        soup = bs(page.content, 'html.parser')

                        # extract links
                        self.lock.acquire()
                        self.extract_links(soup)
                        self.lock.release()
                        
                        log.info('LINKS count:= {}'.format(len(self.LINKS)))
                        verbose(' Number to links:=')
                        verbose('  To be visited: {}'.format(len(self.LINKS)))
                        verbose('  Visited Links: {}'.format(len(self.VISITED_LINKS)))
                        verbose('  Crawled Count: {}'.format(self.CRAWLED_PAGE_COUNT))                        
                        log.debug(pformat(self.LINKS))

                        path_suffix, metadata_record, contents = self.process_page(current_link, soup)
                        verbose('  path: {}'.format(path_suffix))
                        for dir_, content in contents.items():
                            with open('{}/{}'.format(dir_, path_suffix), 'w') as f:
                                f.write('{}'.format(current_link))
                                f.write('\n------------------\n')
                                f.write(content)

                        self.lock.acquire()
                        
                        self.title_file.write(metadata_record + '\n')
                        self.CRAWLED_PAGE_COUNT += 1
                        if len(self.LINKS) < 1 and self.CRAWLED_PAGE_COUNT > self.MAX_COUNT:
                            break_loop = True
                    
                        self.lock.release()
                        
                    except KeyboardInterrupt:
                        raise KeyboardInterrupt

                    except:
                        log.exception(current_link)
                        self.lock.acquire()
                        self.write_state()
                        self.lock.release()
                else:
                    log.info('already visited {}'.format(current_link))
                    verbose('already visited')

        except:
            log.exception('###############')
            
        self.lock.acquire()
        
        self.title_file.close()
        self.write_state()
        
        self.lock.release()
            
