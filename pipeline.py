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
import os
from typing import Callable
from news import json_dir
from news_cnbc import process as process_ng_cnbc, NewsItem_CNBC
from news_reuters import process as process_ng_reuters, NewsItem_Reuters

from news_nlp import process_ng, process_nlp_applied
from news_bmw_docx import convert_ng_nlp_to_docx, docx_out

def process_news_to_docx(ni_cls, process: Callable):
    for front_url in ni_cls.URLS:
        html_path, json_path = process(front_url)
        
        fa, fb = os.path.splitext(os.path.basename(html_path))

        b = os.path.join(json_dir, fa + "--nlp" + fb)
        b_applied = os.path.join(json_dir, fa + "--nlp--applied" + fb)
        
        process_ng(json_path, b, ni_cls.cleanup_content)

        process_nlp_applied(b, b_applied)

        docx_path = os.path.join(docx_out, fa + ".docx")

        convert_ng_nlp_to_docx(b_applied, docx_path)

if __name__ == "__main__":
    for process, ni_cls in [
        [process_ng_cnbc, NewsItem_CNBC],
        [process_ng_reuters, NewsItem_Reuters],
    ]:
        process_news_to_docx(ni_cls, process)