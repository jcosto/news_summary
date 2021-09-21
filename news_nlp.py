"""
header separated using static value (tfidf * semantic similarity < 0.1)
"""
from dataclasses import asdict, dataclass, field
import os
from typing import Callable, List
from news import NewsItem

@dataclass
class NewsItemNLP():
    ni: NewsItem
    content_header_similarity: List = field(default_factory=lambda : list())
    @classmethod
    def from_news_item_dict(cls, d: dict):
        return NewsItemNLP(NewsItem(**d))

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from news_nlp_lemma import tokenizer, token_stop
def get_tfidf(search_terms, documents):
    vectorizer = TfidfVectorizer(stop_words=token_stop, tokenizer=tokenizer)
    doc_vectors = vectorizer.fit_transform([search_terms] + documents)
    cosine_similarities = linear_kernel(doc_vectors[0:1], doc_vectors).flatten()
    document_scores = [item.item() for item in cosine_similarities[1:]]
    return document_scores

from news_nlp_gensim import preprocess, get_doc_similarity_scores
def get_gensim_doc_similarity_scores(search_terms, documents):
    return get_doc_similarity_scores(
        preprocess(search_terms),
        [preprocess(document) for document in documents]
    )

def process_ng(
    ng_json_path, output_json_path,
    content_preprocess_fun: Callable = lambda x_list: x_list
):
    with open(ng_json_path, 'r') as fin:
        nlist = json.load(fin)
    ni_nlp_list = list()
    for ndict in nlist:
        ni_nlp = NewsItemNLP.from_news_item_dict(ndict)

        print(ni_nlp.ni.header)
        content = content_preprocess_fun(ni_nlp.ni.content)
        ds_tfidf = []
        ds_gensim = []
        if content:
            ds_tfidf = get_tfidf(ni_nlp.ni.header, content)
            # pprint(list(zip(ds_tfidf, ni_nlp.ni.content))[:3])
            ds_gensim = get_gensim_doc_similarity_scores(ni_nlp.ni.header, content)
            # pprint(list(zip(ds_gensim, ni_nlp.ni.content))[:3])

        for dst, dsg, c, idx in zip(ds_tfidf, ds_gensim, content, range(len(content))):
            if idx < 3:
                pprint([dst, dsg, c])
            ni_nlp.content_header_similarity.append({
                "ds_tfidf": float(dst),
                "ds_gensim": float(dsg),
                "content": c
            })
        
        d = asdict(ni_nlp)
        # d['ni'] = asdict(d['ni'])

        ni_nlp_list.append(d)
    with open(output_json_path, 'w') as fout:
        json.dump(ni_nlp_list, fout, sort_keys=True, indent=4)
    print(f"saved nlp results to {output_json_path}")
    return ni_nlp_list

import json
from pprint import pprint
from news import json_dir
from news_reuters import NewsItem_Reuters

def get_ng_nlp_from_json(json_path):
    with open(json_path,'r') as fin:
        ng_nlp_list = json.load(fin)
    
    ng_nlp_obj_list = list()
    for ng_nlp_dict in ng_nlp_list:
        ni_nlp = NewsItemNLP(
            NewsItem(**ng_nlp_dict['ni']),
            content_header_similarity=ng_nlp_dict["content_header_similarity"]
        )
        ng_nlp_obj_list.append(ni_nlp)
    return ng_nlp_obj_list

def process_nlp_applied(nlp_json_path, nlp_applied_json_path):
    
    ng_nlp_dict_list = list()
    for ni_nlp in get_ng_nlp_from_json(nlp_json_path):
        
        print(ni_nlp.ni.header)
        summary = list()
        summary_scores = list()
        for ds_ds_c, idx in zip(ni_nlp.content_header_similarity, range(len(ni_nlp.content_header_similarity))):
            if len(summary) == 2:
                break
            if idx < 5:
                ds_t, ds_g, c = ds_ds_c["ds_tfidf"], ds_ds_c["ds_gensim"], ni_nlp.ni.content[idx]
                ds = ds_t * ds_g
                if idx == 0 and ds > 0.1:
                    continue
                # pprint([ds, c[:50]])
                summary.append(c)
                print(c)
                summary_scores.append(ds)
        # pprint(summary)
        print(summary_scores)
        ni_nlp.ni.summary = ' '.join(summary)
        ng_nlp_dict_list.append(asdict(ni_nlp))


    with open(nlp_applied_json_path, 'w') as fout:
        json.dump(ng_nlp_dict_list, fout, sort_keys=True, indent=4)
    
    print(f"saved applied nlp to {nlp_applied_json_path}")


if __name__ == "__main__":
    a = r"D:\dev local\news_summary\out\json\https___www_reuters_com_business_finance_.json"

    fa, fb = os.path.splitext(os.path.basename(a))

    b = os.path.join(json_dir, fa + "--nlp" + fb)
    b_applied = os.path.join(json_dir, fa + "--nlp--applied" + fb)

    # process_ng(a, b,content_preprocess_fun=NewsItem_Reuters.cleanup_content)

    process_nlp_applied(b, b_applied)

    

    
    


