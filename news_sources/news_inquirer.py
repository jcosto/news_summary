from news import NewsGroup, NewsItem, has_class_name, get_page_source, get_filesafe_url
from news import html_dir, json_dir
import bs4
import os
import datetime

class NewsItem_Inquirer(NewsItem):
    BASE_URL = "https://business.inquirer.net"
    URLS = [
        "https://business.inquirer.net"
    ]
    @classmethod
    def yield_news(cls, soup: bs4.BeautifulSoup, base_url: str):
        for s in soup.findAll('div', {"id": "cmr-bg"}):
            # print(s["class"])
            # print(['StoryCollection__story' in c for c in s["class"]])
            # print(s)
            s = s.parent
            # print(s)
            if not s.find("h2") is None:
                header = s.find("h2").text
            else:
                header = s.find("h3").text
            print(s)
            try:
                url = s['onclick'].replace("window.open('", "").replace("','_blank');", "")
            except:
                print("!!")
                print(s)
                url = s.parent['href']

            # if 'onclick' in s:
                
            # else:
                
            #     url = s.parent['href']
            n = NewsItem_Inquirer(
                base_url,
                url,
                s.find("h3").text,
                header,
                ""
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
        a = (
            soup.find("div", {"id": "byline_share"})
            .find("div", {"id": "art_plat"})
        )
        for c in a.find_all("a"):
            c.decompose()
        self.full_date = a.text
        print(self.full_date)
    
    def extract_summary_content(self, soup: bs4.BeautifulSoup):
        summary = list()
        content = list()
        from news import has_class_name
        d = soup.find("div", {"id": "article_content"})
        if not d:
            return
        for d in d.findAll("p"):
            this_text = d.text
            if not this_text is None:
                if len(this_text) == 0:
                    continue
                if "CONTRIBUTED PHOTO" in this_text:
                    continue
                if "Written By:" in this_text:
                    continue
                if "By " in this_text and "@" in this_text:
                    continue
                if "FEATURED STORIES" in this_text:
                    break
                this_text = this_text.replace("ADVERTISEMENT\n\n\n\n\n\n","").strip()
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
        self.date = datetime.datetime.strptime(' '.join(self.full_date.split()[-3:]),r"%B %d, %Y").isoformat()
        # self.content = NewsItem_Inquirer.cleanup_content(self.content)

if __name__ == "__main__":
    for front_url in NewsItem_Inquirer.URLS:
        html_path, json_path, ng = NewsGroup.process(
            NewsItem_Inquirer, front_url,
            html_dir_=html_dir, json_dir_=json_dir
        )