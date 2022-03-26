from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime

class NewsItem_CNN(NewsItem):
    BASE_URL = "https://edition.cnn.com"
    URLS = [
        "https://edition.cnn.com/business"
    ]
    @classmethod
    def yield_news(cls, soup: bs4.BeautifulSoup, base_url: str):
        for s in soup.find('ul', {"class", "cn-list-hierarchical-xs"}).findAll("li"):
            # print(s["class"])
            # print(['StoryCollection__story' in c for c in s["class"]])
            # print(s)
            # print(s)
            print(s.find('a')['href'])
            n = NewsItem_CNN(
                base_url,
                base_url + s.find('a')['href'],
                "",
                s.find("span", {"class": "cd__headline-text"}).text,
                s.find('article',['data-section-name'])
            )
            print(s.find("span", {"class": "cd__headline-text"}).text)
            yield n
    @classmethod
    def cleanup_content(cls, content: list):
        return content
    
    @classmethod
    def cleanup_content_item(cls, c: str, i: int):
        return c

    def extract_header(self, soup: bs4.BeautifulSoup):
        self.header = soup.find("h1", {"class", "pg-headline"}).text
    
    def extract_full_date(self, soup: bs4.BeautifulSoup):
        self.full_date = soup.find("p", {"class", "update-time"}).text
        print(self.full_date)
    
    def extract_summary_content(self, soup: bs4.BeautifulSoup):
        summary = list()
        content = list()
        from news import has_class_name
        d = soup.find("div", {"class": "pg-rail-tall__body"})
        # print(d)
        if not d:
            d = soup.find("div", {"class": "pg-special-article__wrapper"})
        if not d:
            return
        d = d.find("div", {"class": "l-container"})
        for d in d.findAll("div"):
            this_text = None
            if has_class_name(d, ['el__leafmedia']):
                p = d.find('p', {"class": 'zn-body__paragraph'})
                if p:
                    for c in p.find_all("cite"):
                        c.decompose()
                    this_text = p.get_text()
            if has_class_name(d, ['zn-body__paragraph']):
                this_text = d.text
            if not this_text is None:
                if 'A version of this story first appeared in CNN' in this_text:
                    this_text = None
            
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

        if "We're sorry, the page you were looking for cannot be found." in soup.text:
            return None
                
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
        self.date = datetime.datetime.strptime(' '.join(self.full_date.split()[-3:]),r"%B %d, %Y").isoformat()
        self.content = NewsItem_CNN.cleanup_content(self.content)

if __name__ == "__main__":
    for front_url in NewsItem_CNN.URLS:
        html_path, json_path, ng = NewsGroup.process(
            NewsItem_CNN, front_url,
            html_dir_=html_dir, json_dir_=json_dir
        )