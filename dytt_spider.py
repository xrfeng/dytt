import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Process
import pymongo
from requests_study.dytt.config import *

client = pymongo.MongoClient(MONGO_URL,MONGO_PORT)
db = client[MONGO_DB]

def get_soup(url):
    resp = requests.get(url).content.decode('gbk','ignore')
    soup = BeautifulSoup(resp,'lxml')
    return soup

def parse_movie_info(soup):
    pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    info = []
    movies = soup.select('table.tbspan')
    for movie in movies:
        movie_info = {}
        movie_name = movie.select_one('b').get_text()
        movie_link = 'http://www.dytt8.net' + movie.select_one('b > a')['href']
        date = movie.select_one('font').get_text()
        date = re.findall(pattern, date)[0]
        desc = movie.select('tr')[3].get_text()
        movie_info['movie_name'] = movie_name
        movie_info['movie_link'] = movie_link
        movie_info['date'] = date
        movie_info['desc'] = desc
        info.append(movie_info)
    return info

def save_to_mongodb(info):
    for i in info:
        db[MONGO_TABLE].insert(i)

def main():
    urls = ['http://www.dytt8.net/html/gndy/dyzz/list_23_%s.html' % str(i) for i in range(1, 165)]
    for url in urls:
        soup = get_soup(url)
        info = parse_movie_info(soup)
        save_to_mongodb(info)

if __name__ == '__main__':
    main()

