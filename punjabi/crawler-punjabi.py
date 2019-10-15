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

sys.path.append('../')

import config
from crawler import mkdir, verbose
from crawler import Crawler, MultiThreadedCrawler2
from crawler import HTTP, HTTPS
from aliases import GregorianMonthInEnglishShort as MonthAlias

import logging
logging.basicConfig(format=config.CONFIG.FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(config.CONFIG.LOGLEVEL)


uid_ = 0
name = '{}'.format(uid_)
    
class OneIndiaCrawler(MultiThreadedCrawler2):

    def __init__(self, root_url, num_threads=1):
        root_dir= os.path.abspath(__file__)
        root_dir = (os.sep).join(root_dir.split(os.sep)[-2:])
        root_dir = root_dir.replace('crawler-', '').replace('.py', '')

        verbose('root directory for storing data is {}'.format(root_dir))
        
        super().__init__(root_url = root_url,
                         root_dir = root_dir,
                         num_threads = num_threads)

        self.month_alias = MonthAlias()
        
    def extract_year_month(self, page_link, soup):
        global uid_
        year, month = '0000', '00'

        try:
            soup = soup.encode('utf-8')
            timestamp = soup.find(class_='articlePublishDate')
            log.info(timestamp.text)
            if timestamp:
                timestamp = timestamp.text.split()
                #month, year = timestamp[3], timestamp[5]
                year = timestamp[4].replace(",", "")
                month = timestamp[2].lower()
        except:
            log.exception('year and month extraction failed')
            
        return year, month


    def url_filter(self, url):
        use_url = False
        if url.startswith('http'):
            if url.startswith(HTTP + self.ROOT_URL):
                use_url = True
                
            if url.startswith(HTTPS + self.ROOT_URL):
                use_url = True
            else:
                use_url = False
                
        else:
            use_url = True
            

        for ext in ['.jpg', '.png', '.mp4']:
            if url.endswith(ext):
                use_url = False

        return use_url
    
    def process_page(self, url, soup):
        global uid_
        soup = soup.encode('utf-8')
        url = url.encode('utf-8')
        # remove all javascript and stylesheet code
        for script in soup(["script", "style"]): 
            script.extract()

        content = soup.find(class_='oiMiddleMain')
        
        if not content:
            log.error('content extraction failed')
            verbose('content extraction failed')
            log.error('{}'.format(url))
            raise Exception
        else:
            verbose(' Content:=')
            verbose('  size: {}'.format(len(content)))        
            year, month = self.extract_year_month(url, soup)
            log.info('year, month = {}, {}'.format(year, month))

            verbose('  year/month: {}/{}'.format(year, month))
            name = '___'.join(
                url.split('?')[0].split('/')[-2:]
            ).replace('.html', '')

            log.debug(content)
            paras = content.findAll('p')  ; log.debug(pformat(paras))

            path_suffix = '{}/{}/{}.txt'.format(year, self.month_alias[month], name)

            for d in self.SUBDIRS:
                mkdir('{}/{}/{}'.format(d, year, self.month_alias[month]))

            
            page_content  = '\n'.join(p.text for p in paras)
            page_abstract = paras[0].text.strip()
            title         = soup.find('h1')

            breadcrumbs  = soup.find(class_='breadcrump clearfix').findAll('a')
            breadcrumbs  = ','.join([b.text.replace('\n', '').replace('\r', '')
                                for b in breadcrumbs])

            tags = soup.find(class_='tags_head').findAll('a')
            tags = ','.join([b.text.replace('\n', '').replace('\r', '')
                                for b in tags])
                                
            log.info(title.text)
            log.info(breadcrumbs)
            log.info(tags)

            record = '{}|{}|{}|{}|{}'.format(path_suffix.strip(), url, title.text.strip(),
                                breadcrumbs, tags)

            return (path_suffix,
                    record, 
                    {
                        self.ARTICLES_DIR : page_content
                        , self.ABSTRACTS_DIR: page_abstract
                    }
            )


if __name__ == '__main__':
    crawler = OneIndiaCrawler('malayalam.oneindia.com', num_threads=12)
    crawler.initialize_dir_structure()
    crawler.crawl()
