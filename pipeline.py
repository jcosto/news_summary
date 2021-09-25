"""
news page handlers:
news_cnbc
news_reuters

process:
    derive data from news front page url as html and json files
    get document similarity between header and content
    get news summary, applying document similarity measures to skip first content line if similar to header
    convert news data to docx as close as possible to target format

postprocess:
    setup macro to finalize formatting
    apply macro to document
    filter and sort news blocks as required
    combine news blocks between different sources
    copy to final report
"""
import datetime
import os
from typing import List, Union
from news import NewsItem, NewsMinimal, ensure_dirs_exist, html_dir, json_dir, NewsGroup
from news_sources.news_cnbc import NewsItem_CNBC
from news_sources.news_reuters import NewsItem_Reuters
from news_sources.news_cnn import NewsItem_CNN
from news_sources.news_inquirer import NewsItem_Inquirer
from news_sources.news_gma import NewsItem_GMA
from news_sources.news_bworld import NewsItem_BWorld

from news_nlp import process_ng__json, process_nlp_applied__json
from news_bmw_docx import convert_ng_nlp_to_docx, docx_out


def append_filter_date(ni: Union[dict, NewsItem, NewsMinimal]):
        if isinstance(ni, dict):
            return ni['date'][:10] in [now, now_before]
        elif isinstance(ni, NewsItem):
            return ni.date[:10] in [now, now_before]
        elif isinstance(ni, NewsMinimal):
            return ni.date[:10] in [now, now_before]
        raise RuntimeError(f"unhandled object {str(ni.__class__)}")

def process_news_to_docx(
    ni_cls, front_url, html_dir_=html_dir, json_dir_=json_dir, docx_out_=docx_out, use_selenium_ng=False,
    append_filter=None, use_selenium_ni=False
):
    ## OVERRIDING APPEND_FILTER DUE TO PROCESS MULTITHREADING
    if append_filter is None:
        append_filter=append_filter_date
    html_path, json_path, ng = NewsGroup.process(
        ni_cls, front_url,
        html_dir_=html_dir_, json_dir_=json_dir_,
        use_selenium_ng=use_selenium_ng, use_selenium_ni=use_selenium_ni
        
    )
    
    fa, fb = os.path.splitext(os.path.basename(html_path))

    b = os.path.join(json_dir_, fa + "--nlp" + fb)
    b_applied = os.path.join(json_dir_, fa + "--nlp--applied" + fb)
    
    process_ng__json(json_path, b)

    process_nlp_applied__json(b, b_applied)

    docx_path = os.path.join(docx_out_, fa + ".docx")

    convert_ng_nlp_to_docx(b_applied, docx_path, append_filter=append_filter)

from multiprocessing import Process
def process_news_urls_to_docx(
    ni_cls, html_dir_=html_dir, json_dir_=json_dir, docx_out_=docx_out, use_selenium_ng=False,
    append_filter=None, use_selenium_ni=False
):
    p_list: List[Process] = list()
    for front_url in ni_cls.URLS:
        p = Process(
            target=process_news_to_docx,
            args=[ni_cls, front_url],
            kwargs={
                "html_dir_": html_dir_,
                "json_dir_": json_dir_,
                "docx_out_": docx_out_,
                "use_selenium_ng": use_selenium_ng,
                "use_selenium_ni": use_selenium_ni,
                # "append_filter": append_filter, #not passing append_filter due to process multithreading
            }
        )
        p.start()
        p_list.append(p)
        if len(p_list) > 4:
            for p_ in p_list:
                p_.join()
            p_list = list()
    for p_ in p_list:
        p_.join()

from news_corpus_nlp import process_grouped_sorted

if __name__ == "__main__":
    start = datetime.datetime.now()

    root = r"D:\Shared\test\bmw"
    now_dt = datetime.datetime.now()
    now = now_dt.isoformat()[:10]
    now_before = (now_dt - datetime.timedelta(days=1)).isoformat()[:10]
    print(now, now_before)
    input("enter")
    

    hd = os.path.join(root, now, "html")
    jd = os.path.join(root, now, "json")
    dd = os.path.join(root, now, "docx")
    dirs = [hd, jd, dd]
    ensure_dirs_exist(dirs)

    for ni_cls, use_selenium_ng, use_selenium_ni in [
        # [NewsItem_GMA, True, False],
        # [NewsItem_CNBC, False, False],
        # [NewsItem_Reuters, False, False],
        # [NewsItem_CNN, False, False],
        # [NewsItem_Inquirer, False, False],
        [NewsItem_BWorld, False, True],
    ]:
        process_news_urls_to_docx(
            ni_cls, html_dir_=hd, json_dir_=jd, docx_out_=dd,
            use_selenium_ng=use_selenium_ng,
            use_selenium_ni=use_selenium_ni,
            append_filter = append_filter_date
        )
    
    process_grouped_sorted(
        json_dir_=jd, docx_out_=dd,
        append_filter = append_filter_date
    )

    end = datetime.datetime.now()

    duration = (end-start).total_seconds()
    print(f"{duration}s ~{int(duration/60)}m ~{int(duration/60/60)}h")
