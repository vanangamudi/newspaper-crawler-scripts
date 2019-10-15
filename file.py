from bs4 import BeautifulSoup as bs
import requests
page=requests.get("http://goenkaar.com/?p=8566")
soup=bs(page.text,'html.parser')
metas=soup.find_all('meta', itemprop="datePublished")
content=map(lambda x:x.attrs,metas)

print(list(content)[0]['content'])
content=map(lambda x:x.attrs,metas)
date = list(content)[0]['content']

print(date)