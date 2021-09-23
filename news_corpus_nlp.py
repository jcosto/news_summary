from pprint import pprint

from gensim.corpora.dictionary import Dictionary
from news_nlp import get_tfidf
from news_nlp_gensim import preprocess, get_doc_similarity_scores
from news import json_dir
import os
import json

urls = list()
url_dict = dict()
docs = list()

for f in os.listdir(json_dir):
    fp = os.path.join(json_dir, f)
    if os.path.isfile(fp) and '--nlp--applied' in fp:    
        print(f"loading {fp}")
        with open(fp, 'r', encoding='utf8') as fin:
            n_list = json.load(fin)
        for n in n_list:
            # pprint(n)
            doc = n['ni']['header'] + ' '+ n['ni']['summary']
            urls.append(n['ni']['url'])
            url_dict[n['ni']['url']] = doc
            docs.append(doc)

docs_idx = [[i,d] for i,d in enumerate(docs)]

# DOCUMENT SIMILARITY
found_ids = set()
found_groups = list()
def process_doc(docs_idx, idx, doc):
    these_docs = [[i,d] for i,d in docs_idx if i != idx and i not in found_ids]
    this_group = [[idx, doc]]
    found_ids.add(idx)
    if these_docs:
        ds_tfidf = get_tfidf(doc ,[i_d[1] for i_d in these_docs])
        ds_gensim = [1] * len(ds_tfidf)
        # ds_gensim = get_doc_similarity_scores(
        #     preprocess(doc), [preprocess(i_d[1]) for i_d in these_docs]
        # )
        # print(document_scores[0])
        i_s_d = [
            [i_d[0], s_tfidf, s_gensim, i_d[1]]
            for i_d, s_tfidf, s_gensim
            in zip(these_docs, ds_tfidf, ds_gensim)
            # if s_tfidf * s_gensim > 0.1
            if s_tfidf * s_gensim > 0.2
        ]
        i_s_d.sort(reverse=True, key=lambda x: x[1] * x[2])
        if i_s_d:
            print(doc[:100])
            # c = 0
            for i, s_tfidf, s_gensim, d in i_s_d:
                # c += 1
                # if c > 5:
                #     break
                found_ids.add(i)
                this_group.append([i, d])
                print("--", i, round(s_tfidf * s_gensim,3), d[:100])
            # input("enter to continue...")
    found_groups.append(this_group)

for idx, doc in enumerate(docs):
    process_doc(docs_idx, idx, doc)


    
print(f"found {len(docs_idx)} docs, {len(found_groups)} groups")

