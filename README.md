# Newspaper Crawler Scripts
Set of scripts for crawling Newspapers Websites. Please find the available scripts below

## Setup

`pip3 install -r requirements.txt`  

## Todo
[ ] Extract common code into a decorator


## Contribute
Scripts for more news websites are welcome. Please save the text scraped in UTF-8 encoding. Please refer to the [newspapers list file](https://github.com/vanangamudi/newspaper-crawler-scripts/blob/master/newspapers.csv) and pick one to scrape.


## Latest Script  

`crawler-oneindia.py` under malayalam has the latest code, you can use this a template for future crawlers.

## Directory Structure

    <newspaper_name>
      title.list --> acts as a index for other directories.
      articles
      -- 2018
      ---- Dec
      ---- May
      -- 2017
      ---- Jun
      ---- Aug
      -- 2016
      ---- Oct
      ---- Jan
      abstracts
      -- 2018
      ---- Dec
      ---- May
      -- 2017
      ---- Jun
      ---- Aug
      -- 2016
      ---- Oct
      ---- Jan  
      


## Available scripts.
### Tamil  ###
| Site               | URL                            | script                               |
|--------------------|--------------------------------|--------------------------------------|
|  Nakkheeran        | http://nakkheeran.in/          | tamil/crawler-nakkheeran.py          |
| Dailythanthi       | http://dailythanthi.com/       | tamil/crawler-dailythanthi.py        |
| Tamil The Hindu    | http://tamil.thehindu.com/     | tamil/crawler-tamil-hindu.py         |
| Puthiyathalaimurai | http://puthiyathalaimurai.com/ |  tamil/crawler-puthiyathalaimurai.py |
| Dinamani           | http://dinamani.com/           |  tamil/crawler-dinamani.py           |


### Malayalam ###
| Site               | URL                            | script                               |
|--------------------|--------------------------------|--------------------------------------|
|  Manorama          | http://www.manoramaonline.com/ | malayalam/crawler-manorama.py        |
|  Asianet News      | https://www.asianetnews.com/   | malayalam/crawler-asianet.py         |
|  One India         | https://malayalam.oneindia.com/| malayalam/crawler-oneindia.py        |


### Bengali ###
| Site                   | URL                         | script                                |
|------------------------|-----------------------------|---------------------------------------|
|  Ananadabazar          | https://www.anandabazar.com | Bengali/crawler-anandabazar.py        |
|  Aajkal                | https://www.aajkaal.in      | Bengali/crawler-aajkal.py             |



### Konkani
| Site               | URL                            | script                               |
|--------------------|--------------------------------|--------------------------------------|
|  Konkani Kaniyo          | http://konkani-kaniyo-in-nagri.blogspot.com | konkani/crawler-konkani-kaniyo.py        |


### Marathi 
| Site               | URL                                            | script                               |
|--------------------|------------------------------------------------|--------------------------------------|
|  Lokmat            | http://www.lokmat.com/                         | marathi/crawler-lokmat.py            |
|  Maharashtratimes  | https://maharashtratimes.indiatimes.com/       | marathi/crawler-maharashtratimes.py  |
|  Loksatta          | https://www.loksatta.com                       | marathi/crawler-loksatta.py          |
|  ABPmajha          | https://abpmajha.abplive.in                    | marathi/crawler-abpmajha.py          |

