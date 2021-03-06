"""
gma loads pretty slow using selenium
"""
from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime
found_urls = set()
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
            if url in found_urls:
                continue
            found_urls.add(url)

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
            this_text = d.text.strip()
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
        try:
            self.extract_header(soup)
            
            self.extract_full_date(soup)

            self.extract_summary_content(soup)
        except:
            return None

        return self
        
    def cleanup_data(self):
        print(' '.join(self.full_date.split()[-3:]))
        # input("enter to continue")
        self.date = datetime.datetime.strptime(self.full_date[:10],"%Y-%m-%d").isoformat()
        # self.content = NewsItem_Inquirer.cleanup_content(self.content)

if __name__ == "__main__":
    for front_url in NewsItem_GMA.URLS:
        html_path, json_path, ng = NewsGroup.process(
            NewsItem_GMA, front_url,
            html_dir_=html_dir, json_dir_=json_dir
        )