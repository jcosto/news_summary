"""
todo:
(DONE) word formatting from python (python-docx)
(DONE) tf-idf and semantic similarity on summary sentences to prevent repeating article header
ph vs ROW news: how to get geographic source of data from article?
tf-idf/semantic similarity to rank news based on duplication among news sources

finished handlers
https://www.reuters.com/business/finance/
https://www.cnbc.com/finance/

todo handlers
https://www.bworldonline.com/category/top-stories/
https://www.bworldonline.com/category/banking-finance/
https://www.bworldonline.com/category/economy/
https://edition.cnn.com/business

https://business.inquirer.net/
https://www.gmanetwork.com/news/money/

maybe todo
https://www.manilatimes.net/business


errors:
due to reuse of raw content in nlp summary, reuters has extra info not needed. content cleanup doesn't seem to work
"""
from pprint import pprint
from typing import Callable, List
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
import time
import os

def get_page_source(url, dst, sleep_s=0, hold_proc=True):
    if os.path.exists(dst):
        with open(dst,'r', encoding='utf8') as fin:
            ret = fin.read()
        if len(ret) > 0:
            return ret
    
    driver = webdriver.Edge()
    driver.get(url)
    page_source = driver.page_source
    if sleep_s > 0:
        time.sleep(sleep_s)
    
    with open(dst, 'w', encoding='utf8') as fout:
        fout.write(page_source)
    
    if hold_proc:
        input("pausing execution, press enter to continue...")

    driver.quit()
    return page_source

def get_filesafe_url(url):
    return url.replace(":","_").replace("/","_").replace(".","_")

from dataclasses import dataclass, asdict, field
import datetime
import bs4
import json

@dataclass
class NewsGroup():
    base_url: str
    url: str
    page_html_dst: str
    page_json_dst: str
    
    def extract_soup(self, yield_news: Callable, sleep_s=0, hold_proc=True):
        src_html_path = self.page_html_dst
        page_source = get_page_source(
            self.url, src_html_path,
            sleep_s=sleep_s, hold_proc=hold_proc
        )

        soup = bs4.BeautifulSoup(page_source, features='html.parser')
        
        self.news_item__list = list()
        for n in yield_news(soup, self.base_url):
            self.news_item__list.append(n)
        
        self.save_json()
        
        for n in self.news_item__list:
            yield n
    
    def save_json(self):
        with open(self.page_json_dst, 'w') as fout:
            json.dump(
                [asdict(i) for i in self.news_item__list],
                fout, sort_keys=True, indent=4
            )
    

@dataclass
class NewsItem():
    base_url: str
    url: str
    date: str
    header: str
    section: str
    front_page_summary: str = None
    summary: str = None
    full_date: str = None
    dt: datetime.datetime = None
    content: List = field(default_factory=lambda : list())
    content_raw: List = field(default_factory=lambda : list())
    @classmethod
    def yield_news_reuters(cls, soup: bs4.BeautifulSoup, base_url: str):
        pass

def has_class_name(s, c_ref_list):
    try:
        meron = list()
        for c_ref in c_ref_list:
            meron.append(sum([c_ref in c for c in s["class"]]) > 0)
        return len(meron) == sum(meron)
    except KeyError:
        return False
    
dirs = list()
out_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'out')
dirs.append(out_dir)
html_dir = os.path.join(out_dir, "html")
dirs.append(html_dir)
json_dir = os.path.join(out_dir, "json")
dirs.append(json_dir)

def get_filesafe_url(url: str):
    return url.replace(":","_").replace("/","_").replace(".","_")

for d in dirs:
    if not os.path.exists(d):
        os.makedirs(d)

@dataclass
class NewsMinimal():
    url: str
    header: str
    summary: str
    doc: str