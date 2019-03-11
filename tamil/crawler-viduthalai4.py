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


from crawler import mkdir, verbose
from crawler import Crawler, MultiThreadedCrawler2
from crawler import HTTP, HTTPS
from aliases import GregorianMonthInTamilAlias as MonthAlias

import logging
logging.basicConfig(format=config.CONFIG.FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(config.CONFIG.LOGLEVEL)


uid_ = 0
name = '{}'.format(uid_)
    
class ViduthalaiCrawler(MultiThreadedCrawler2):

    def __init__(self, root_url, num_threads=1):
        root_dir= os.path.abspath(__file__)
        root_dir = '/'.join(root_dir.split('/')[-2:])
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
            timestamp = soup.find(class_='date')
            timestamp = timestamp.find(class_='created')
            log.info(timestamp.text)
            m = re.search('.*, \d+ (.*) (\d{4})', timestamp.text.strip())
            if m:
                log.debug(pformat(m))
                month, year = m.groups()
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
        # remove all javascript and stylesheet code
        for script in soup(["script", "style"]): 
            script.extract()

        content = soup.find(class_='article')

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
            title         = soup.find(class_='headline')
            record        = '{}|{}|{}'.format(path_suffix.strip(), url, title.text.strip())

            log.info(title.text)

            return (path_suffix,
                    record, 
                    {
                        self.ARTICLES_DIR : page_content
                        , self.ABSTRACTS_DIR: page_abstract
                    }
            )


if __name__ == '__main__':
    crawler = ViduthalaiCrawler('viduthalai.in', num_threads=12)
    crawler.initialize_dir_structure()
    crawler.crawl()
