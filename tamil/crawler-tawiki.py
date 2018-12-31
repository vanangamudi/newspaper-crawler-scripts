# -*- coding: utf-8 -*-
import urllib
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys
ROOT_URL = 'https://ta.wikipedia.org'
page = requests.get("https://ta.wikipedia.org/wiki/விக்கிப்பீடியா:முதற்பக்கக்_கட்டுரைகள்")
soup = bs(page.content, 'html.parser')
yearly = soup.find(class_='mw-parser-output').select("div li")

#print(yearly[0].prettify(), type(yearly[0]))

for year in yearly:
    print('processing: {}'.format(urllib.parse.unquote(year.a['href'])))
    ypage = requests.get('{}{}'.format(ROOT_URL, year.a['href']))
    ysoup = bs(ypage.content, 'html.parser')
    pages = ysoup.find(class_='mw-parser-output').find_all('p')

    page_name = ''
    for wp in tqdm(pages, desc=page_name):
        try:
            page_name = urllib.parse.unquote(wp.a['href'])
            print('processing: {}'.format(page_name))
            wpage = requests.get('{}{}'.format(ROOT_URL, wp.a['href']))
            wsoup = bs(wpage.content, 'html.parser')
            content = '\n\n'.join(i.text for i in wsoup.find(class_='mw-parser-output').find_all('p'))

            #print(content)

            with open('tawiki/{}.wiki'.format(page_name.split('/')[-1]), 'w') as f:
                f.write('{}\n------------------\n'.format(page_name))
                f.write(content)
        except:
            print(sys.exc_info())
