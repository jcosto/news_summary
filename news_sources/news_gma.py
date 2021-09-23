"""
gma loads pretty slow
"""
from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime

class NewsItem_GMA(NewsItem):
    BASE_URL = "https://www.gmanetwork.com/"
    URLS = [
        "https://www.gmanetwork.com/news/money"
    ]
    @classmethod
    def yield_news(cls, soup: bs4.BeautifulSoup, base_url: str):
        for s in soup.findAll('a', {"class": "story_link"}):
            # print(s["class"])
            # print(['StoryCollection__story' in c for c in s["class"]])
            # print(s)
            # print(s)
            try:
                section = s.find("div", {"class": "subsection"}).text
            except:
                section = None

            url = s['href']
            if url.endswith("/photo/"):
                continue

            n = NewsItem_GMA(
                base_url,
                s['href'],
                "",
                s.find("div", {"class": "story_title"}).text,
                section
            )
            print(s['href'])
            print("------")
            yield n
        
    @classmethod
    def cleanup_content(cls, content: list):
        return content
    
    @classmethod
    def cleanup_content_item(cls, c: str, i: int):
        return c

    def extract_header(self, soup: bs4.BeautifulSoup):
        self.header = soup.find("h1", {"class": "story_links"}).text
    
    def extract_full_date(self, soup: bs4.BeautifulSoup):
        self.full_date = soup.find("div", {"class": "article-time"}).find("time")['datetime']
        print(self.full_date)
    
    def extract_summary_content(self, soup: bs4.BeautifulSoup):
        summary = list()
        content = list()
        from news import has_class_name
        d = soup.find("div", {"class": "story_main"})
        if not d:
            return
        for d in d.children:
            if not d.name in ['p', 'ul', 'li']:
                continue
            this_text = d.text
            if not this_text is None:
                if len(this_text) == 0:
                    continue
                if len(summary) < 2:
                    print(this_text)
                    summary.append(this_text)
                content.append(this_text)
        
        self.summary = ' '.join(summary)
        print("summary", self.summary)
        
        self.content = list(content)
        self.content_raw = list(content)

        # print("content", self.content)

    def extract_news_content(
        self,
        news_content_html_dir,
        sleep_s=0, hold_proc=True
    ):
        url = self.url
        page_source = get_page_source(
            url, os.path.join(news_content_html_dir, get_filesafe_url(url)),
            sleep_s=sleep_s, hold_proc=hold_proc,
            # use_selenium=True
        )
        soup = bs4.BeautifulSoup(page_source, features='html.parser')
        
        self.extract_header(soup)
        
        self.extract_full_date(soup)

        self.extract_summary_content(soup)
        
    def cleanup_data(self):
        print(' '.join(self.full_date.split()[-3:]))
        # input("enter to continue")
        self.date = datetime.datetime.strptime(self.full_date[:10],"%Y-%m-%d").isoformat()
        # self.content = NewsItem_Inquirer.cleanup_content(self.content)

def process_item(n: NewsItem_GMA):
    print("------------")
    print(n.base_url)
    print(n.url)
    
    n.extract_news_content(html_dir, hold_proc=False)
    n.cleanup_data()
    
    for i, j in zip(n.content, n.content_raw):
        print("-- " + i)
        print("++ " + j)
    # input("enter to continue...")


from threading import Thread
def process(front_url):
    front_filesafe = front_url.replace(":","_").replace("/","_").replace(".","_")
    front_html = os.path.join(html_dir, front_filesafe)
    front_json = os.path.join(json_dir, front_filesafe)
    ng = NewsGroup(NewsItem_GMA.BASE_URL, front_url, front_html, front_json)
    t_list = list()
    for n in ng.extract_soup(NewsItem_GMA.yield_news, hold_proc=False):
        process_item(n)
    #     t = Thread(target=process_item, args=[n], daemon=True)
    #     t_list.append(t)
    #     t.start()
    # #     if len(t_list) > 4:
    # #         for t_ in t_list:
    # #             t_.join()
    # #         t_list = list()
    # # for t in t_list:
    #     t.join()

    ng.save_json()
    return front_html, front_json

if __name__ == "__main__":
    for front_url in NewsItem_GMA.URLS:
        html_path, json_path = process(front_url)