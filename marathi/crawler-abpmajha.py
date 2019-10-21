# -*- coding: utf-8 -*-
import logging
import sys
sys.path.append('../')

from aliases import GregorianMonthInEnglishShort as MonthAlias
from crawler import HTTP, HTTPS
from crawler import Crawler, MultiThreadedCrawler2
from crawler import mkdir, verbose
import config
import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import time
from pprint import pprint, pformat


logging.basicConfig(format=config.CONFIG.FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(config.CONFIG.LOGLEVEL)


uid_ = 0
name = '{}'.format(uid_)


class AbpMajhaCrawler(MultiThreadedCrawler2):

    def __init__(self, root_url, num_threads=1):
        root_dir = os.path.abspath(__file__)
        root_dir = (os.sep).join(root_dir.split(os.sep)[-2:])
        root_dir = root_dir.replace('crawler-', '').replace('.py', '')

        verbose('root directory for storing data is {}'.format(root_dir))

        super().__init__(root_url=root_url,
                         root_dir=root_dir,
                         num_threads=num_threads)

        self.month_alias = MonthAlias()

    def extract_year_month(self, page_link, soup):
        global uid_
        year, month = '0000', '00'

        try:
            timestamp = soup.find(class_='date_article text-left mt-0 mt-md-2').findAll('span')[4]
            log.info(timestamp.text)
            m = re.search('(.*) (.*) (.*) (.*) (.*)',
                          timestamp.text.strip())
            if m:
                log.debug(pformat(m))
                g = m.groups()
                month = g[1].lower()
                year = g[2]
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
        for script in soup(["script", "style","iframe"]):
            script.extract()

        content = soup.find(class_='_picCon _disable_copy _munchDiscuss')

        if not content:
            log.error('content extraction failed')
            verbose('content extraction failed')
            log.error('{}'.format(url))
            raise Exception
        else:
            try:
                verbose('content extraction Success')#New
                verbose(' Content:=')                
                verbose('  size: {}'.format(len(content)))
                year, month = self.extract_year_month(url, soup)
                log.info('year, month = {}, {}'.format(year, month))

                verbose('  year/month: {}/{}'.format(year, month))
                name = '___'.join(
                    url.split('?')[0].split('/')[-2:]
                ).replace('.html', '')

                log.debug(content)
                # paras = content.findAll('p')
                # log.debug(pformat(paras))
                
                path_suffix = '{}/{}/{}.txt'.format(year,
                                                    self.month_alias[month], name)

                for d in self.SUBDIRS:
                    mkdir('{}/{}/{}'.format(d, year, self.month_alias[month]))

                # page_content = '\n'.join(p.text for p in paras)
                page_content = content.text.replace(u'\xa0', '')
                page_abstract = soup.find(class_='small_intro').text.strip()
                title = soup.find(class_='arH LineHiet')

                breadcrumbs = soup.find(class_='breadcrumbs').findAll('a')
                breadcrumbs = ','.join([b.text.replace('\n', '').replace('\r', '')
                                        for b in breadcrumbs])
                
                tags = soup.find(class_='_tag pb-0 pb-md-3').findAll('a')
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
                            self.ARTICLES_DIR: page_content, self.ABSTRACTS_DIR: page_abstract
                        }
                        )
            except :
                verbose("Error while processing")


if __name__ == '__main__':
    # Keeping one thread for debugging
    crawler = AbpMajhaCrawler('abpmajha.abplive.in', num_threads=1)
    crawler.initialize_dir_structure()
    crawler.crawl()
