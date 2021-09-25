"""
gma loads pretty slow
"""
from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime
found_urls = set()
class NewsItem_BWorld(NewsItem):
    BASE_URL = "https://www.bworldonline.com/"
    URLS = [
        "https://www.bworldonline.com/category/top-stories/",
        "https://www.bworldonline.com/category/banking-finance/",
        "https://www.bworldonline.com/category/economy/",
        "https://www.bworldonline.com/category/corporate/",
        "https://www.bworldonline.com/category/stock-market/",
    ]
    @classmethod
    def yield_news(cls, soup: bs4.BeautifulSoup, base_url: str):
        for s in soup.find("div", {"class": "td-subcategory-header"}).findAll('div', {"class": "td-module-thumb"}):
            s = s.parent
            # print(s)
            url = s.find("a")["href"]
            if url in found_urls:
                continue
            found_urls.add(url)
            header = s.find("h3", {"class": "entry-title"}).text
            section = s.find("a", {"class": "td-post-category"}).text

            n = NewsItem_BWorld(
                base_url,
                url,
                "",
                header,
                section
            )
            print(url)
            print("------")
            yield n
        for s in soup.find("div", {"class": "td-ss-main-content"}).findAll('div', {"class": "td_module_10"}):
            url = s.find("a", {"class": "td-image-wrap"})["href"]
            if url in found_urls:
                continue
            found_urls.add(url)
            header = s.find("h3", {"class": "entry-title"}).text
            section = ""
            

            n = NewsItem_BWorld(
                base_url,
                url,
                "",
                header,
                section
            )
            print(url)
            print("------")
            yield n
        
    @classmethod
    def cleanup_content(cls, content: list):
        return content
    
    @classmethod
    def cleanup_content_item(cls, c: str, i: int):
        return c

    def extract_header(self, soup: bs4.BeautifulSoup):
        self.header = soup.find("h1", {"class": "entry-title"}).text
    
    def extract_full_date(self, soup: bs4.BeautifulSoup):
        self.full_date = soup.find("time", {"class": "entry-date"})['datetime']
        print(self.full_date)
    
    def extract_summary_content(self, soup: bs4.BeautifulSoup):
        summary = list()
        content = list()
        from news import has_class_name
        content_classes = ["td-post-content", "td-pb-padding-side"]
        d = None
        d__ = soup.find_all("div", {"class": content_classes})
        for d_ in d__:
            if has_class_name(d_, content_classes):
                d = d_
                break
        if not d:
            raise RuntimeError(f"no content found for {self.url}")
        for d in d.children:
            if not d.name in ['p', 'ul', 'li']:
                continue
            this_text = d.text
            if this_text.startswith("By ") and ", Reporter" in this_text:
                continue
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
        
        self.extract_header(soup)
        
        self.extract_full_date(soup)

        self.extract_summary_content(soup)

        return self
        
    def cleanup_data(self):
        print(' '.join(self.full_date.split()[-3:]))
        # input("enter to continue")
        self.date = datetime.datetime.strptime(self.full_date[:10],"%Y-%m-%d").isoformat()
        # self.content = NewsItem_Inquirer.cleanup_content(self.content)

if __name__ == "__main__":
    for front_url in NewsItem_BWorld.URLS:
        html_path, json_path, ng = NewsGroup.process(
            NewsItem_BWorld, front_url,
            html_dir_=html_dir, json_dir_=json_dir
        )