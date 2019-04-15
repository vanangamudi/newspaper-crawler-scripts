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
| Dinamani           | http://dinamani.com/           |  tamil/crawler-dinamani.py           |


### Malayalam
| Site               | URL                            | script                               |
|--------------------|--------------------------------|--------------------------------------|
|  Manorama          | http://www.manoramaonline.com/ | malayalam/crawler-manorama.py        |


## Contribute
Scripts for more news websites are welcome. Please save the text scraped in UTF-8 encoding. Please refer to the [newspapers list file](https://github.com/vanangamudi/newspaper-crawler-scripts/blob/master/newspapers.csv) and pick one to scrape.

## Todo
[ ] Extract common code into a decorator

## Running the script
Scripts are usually run under the directory where it lives, but the config.py file is the root directory.

Please add `..` in PYTHONPATH so that, config in the root directory is accessible to the script. [ How's the crawler script ran ? #3](https://github.com/vanangamudi/newspaper-crawler-scripts/issues/3)

`$ export PYTHONPATH=$PYTHONPATH:..`

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
      
