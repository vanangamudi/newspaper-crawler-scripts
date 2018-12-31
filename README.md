# Newspaper Crawler Scripts
Set of scripts for crawling newspaper websites. Please find the available scripts below

## Available scripts.
### Tamil
| Site               | URL                            | script                               |
|--------------------|--------------------------------|--------------------------------------|
|  Nakkheeran        | http://nakkheeran.in/          | tamil/crawler-nakkheeran.py          |
| Dailythanthi       | http://dailythanthi.com/       | tamil/crawler-dailythanthi.py        |
| Tamil The Hindu    | http://tamil.thehindu.com/     | tamil/crawler-tamil-hindu.py         |
| Puthiyathalaimurai | http://puthiyathalaimurai.com/ |  tamil/crawler-puthiyathalaimurai.py |

## Contribute
Scripts for more news websites are welcome. Please save the text scraped in UTF-8 encoding.

## Todo
[ ] Extract common code into a decorator

## Directory structure

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
      
