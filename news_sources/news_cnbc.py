from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime

class NewsItem_CNBC(NewsItem):
    BASE_URL = "https://www.cnbc.com"
    URLS = [
        "https://www.cnbc.com/finance/"
    ]
    @classmethod
    def yield_news(cls, soup: bs4.BeautifulSoup, base_url: str):
        for s in soup.findAll("div"):
            # print(s["class"])
            # print(['StoryCollection__story' in c for c in s["class"]])
            if has_class_name(s, ["Card-titleAndFooter"]):
                # print(s)
                a = s.findAll("a", {"class": "Card-title"})[0]
                n = NewsItem_CNBC(
                    base_url,
                    a["href"],
                    s.findAll("span", {"class": "Card-time"}),
                    a.findAll("div")[0].text,
                    ""
                )
                yield n
    @classmethod
    def cleanup_content(cls, content: list):
        return content
    
    @classmethod
    def cleanup_content_item(cls, c: str, i: int):
        return c

    def extract_header(self, soup: bs4.BeautifulSoup):
        self.header = soup.find("div", {"class", "ArticleHeader-headerContentContainer"}).find("h1").text
    
    def extract_full_date(self, soup: bs4.BeautifulSoup):
        self.full_date = soup.find("div", {"class", "ArticleHeader-headerContentContainer"}).find("time")["datetime"]
        print(self.full_date)
    
    def extract_summary_content(self, soup: bs4.BeautifulSoup):
        summary = list()
        content = list()
        d = soup.find("div", {"class": "group"})
        if not d:
            return
        for d in soup.findAll("div", {"class": "group"}):
            for p in d.findAll("p"):
                if "Check out the companies making headlines before the bell:" in p.text:
                    continue
                elif "Check out the companies making headlines in midday trading." in p.text:
                    continue
                elif "Take a look at some of the biggest movers in the premarket:" in p.text:
                    continue
                if len(summary) < 2:
                    print(p.text)
                    summary.append(p.text)
                content.append(p.text)
        
        self.summary = ' '.join(summary)
        print(self.summary)
        self.content = list(content)
        self.content_raw = list(content)

    def extract_news_content(
        self,
        news_content_html_dir,
        sleep_s=0, hold_proc=True,
        use_selenium=False
    ):
        url = self.url
        page_source = get_page_source(
            url, os.path.join(news_content_html_dir, get_filesafe_url(url)),
            sleep_s=sleep_s, hold_proc=hold_proc,
            use_selenium=use_selenium
        )
        soup = bs4.BeautifulSoup(page_source, features='html.parser')
        
        if "We're sorry, the page you were looking for cannot be found." in soup.text:
            return None

        a = soup.find("a", {"class": "ArticleHeader-eyebrow"})
        if a:
            self.section = a.text
        
        self.extract_header(soup)

        self.extract_full_date(soup)

        self.extract_summary_content(soup)

        return self
        
    def cleanup_data(self):
        self.date = datetime.datetime.strptime(self.full_date[:10],"%Y-%m-%d").isoformat()
        self.content = NewsItem_CNBC.cleanup_content(self.content)

if __name__ == "__main__":
    for front_url in NewsItem_CNBC.URLS:
        html_path, json_path, ng = NewsGroup.process(
            NewsItem_CNBC, front_url,
            html_dir_=html_dir, json_dir_=json_dir
        )