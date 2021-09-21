from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime

class NewsItem_Reuters(NewsItem):
    @classmethod
    def yield_news(cls, soup: bs4.BeautifulSoup, base_url: str):
        story_collections = soup.findAll("div")
        for s in story_collections:
            # print(s["class"])
            # print(['StoryCollection__story' in c for c in s["class"]])
            if has_class_name(s, ["StoryCollection__hero"]):
                # print(s)
                for a in s.findAll("a", {"class": "story-card"}):
                    # print(a)
                    # print(a.prettify())
                    # print(a["href"])
                    # print(a.findAll("h3")[0].text)
                    # print(a.findAll("span")[0].text)
                    # print(a.findAll("p")[0].text)
                    n = NewsItem_Reuters(
                        base_url,
                        base_url + a["href"],
                        a.findAll("span")[0].text,
                        a.findAll("h3")[0].text,
                        "Finance",
                        front_page_summary=a.findAll("p")[0].text
                    )
                    yield n
            if has_class_name(s, ["StoryCollection__story"]):
                # print(s)
                for a in s.findAll("a", {"class": "story-card"}):
                    # print(a.prettify())
                    # print(a["href"])
                    # print(a.findAll("span")[0].text)
                    # print(a.findAll("h6")[0].text)
                    # print(a.findAll("time")[0].text)
                    n = NewsItem_Reuters(
                        base_url,
                        base_url + a["href"],
                        a.findAll("time")[0].text,
                        a.findAll("h6")[0].text,
                        a.findAll("span")[0].text
                    )
                    yield n
    @classmethod
    def cleanup_content(cls, content: list):
        c_list = list()
        for i, c in enumerate(content):
            c_list.append(cls.cleanup_content_item(c, i))
        return c_list
    
    @classmethod
    def cleanup_content_item(cls, c: str, i: int):
        c_ = c
        if i == 0:
            try:
                c_ = c_.split("(Reuters) - ")[1]
            except IndexError:
                pass
        if c_.endswith("read more "):
            c_ = c_[:len("read more ")]
        return c_

    def extract_header(self, soup: bs4.BeautifulSoup):
        for d in soup.findAll("h1"):
            # print(d)
            if has_class_name(d, ["Heading__base"]):
                # print(d.prettify())
                print(d.text) #header
                self.header = d.text
                break
    
    def extract_full_date(self, soup: bs4.BeautifulSoup):
        for d in soup.findAll("time"):
            # print(d)
            if has_class_name(d, ["ArticleHeader__dateline"]):
                # print(d.prettify())
                full_time = list()
                for d1 in d.findAll("span"):
                    print(d1.text) #full_time
                    full_time.append(d1.text)
                self.full_date = ','.join(full_time)
                break
    
    def extract_summary_content(self, soup: bs4.BeautifulSoup):
        summary = list()
        content = list()
        for d in soup.findAll("div"):
            if has_class_name(d, ["ArticleBody__content"]):
                for p in d.findAll("p"):
                    if len(summary) < 2:
                        print(p.text)
                        summary.append(p.text)
                    content.append(p.text)
        self.summary = ' '.join(summary)
        self.content = content

    def extract_news_content(self, news_content_html_dir, sleep_s=0, hold_proc=True):
        url = self.url
        page_source = get_page_source(
            url, os.path.join(news_content_html_dir, get_filesafe_url(url)),
            sleep_s=sleep_s, hold_proc=hold_proc
        )
        soup = bs4.BeautifulSoup(page_source, features='html.parser')
        
        self.extract_header(soup)

        self.extract_full_date(soup)

        self.extract_summary_content(soup)
        
    def cleanup_data(self):
        n = self
        n.date = datetime.datetime.strptime(','.join(n.full_date.split(",")[:2]), r"%B %d, %Y").isoformat()
        n.summary = n.summary.split("(Reuters) - ")[1]

if __name__ == "__main__":
    front_url = "https://www.reuters.com/business/finance/"
    front_filesafe = front_url.replace(":","_").replace("/","_").replace(".","_")
    front_html = os.path.join(html_dir, front_filesafe + ".html")
    front_json = os.path.join(json_dir, front_filesafe + ".json")
    ng = NewsGroup("https://www.reuters.com", front_url, front_html, front_json)
    for n in ng.extract_soup(NewsItem_Reuters.yield_news, hold_proc=False):
        print(n.base_url)
        print(n.url)
        n.extract_news_content(html_dir, hold_proc=False)
        n.cleanup_data()
    ng.save_json()