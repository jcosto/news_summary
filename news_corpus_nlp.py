from pprint import pprint

from gensim.corpora.dictionary import Dictionary
from news_nlp import get_tfidf
from news_nlp_gensim import preprocess, get_doc_similarity_scores
from news import json_dir
import os
import json
from news import NewsMinimal

urls = list()
url_dict = dict()
docs = list()
nm_list = list()
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
            nm_list.append(NewsMinimal(
                n['ni']['url'], n['ni']['header'], n['ni']['summary'], doc
            ))

docs_idx = [[i,d] for i,d in enumerate(docs)]

# DOCUMENT SIMILARITY
found_ids = set()
group_sets = list()
def process_doc(docs_idx, idx, doc):
    these_docs = [
        [i,d] for i,d in docs_idx if i != idx
        # and i not in found_ids
    ]
    this_group_set = set([idx])
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
            # if s_tfidf * s_gensim > 0.2
            # if s_tfidf * s_gensim > 0.3145949151248746 # s, Kmeans min of top 5
            # if s_tfidf * s_gensim > 0.21288589997820936 # SVM plane using s, Kmeans label of top 5
            # if s_tfidf * s_gensim > 0.15340770596103756 # SVM plane using s, Kmeans label of all scores
            if s_tfidf * s_gensim > 0.3372818715488682 # more docs
        ]
        i_s_d.sort(reverse=True, key=lambda x: x[1] * x[2])
        if i_s_d:
            print(doc[:100])
            c = 0
            for i, s_tfidf, s_gensim, d in i_s_d:
                c += 1
                if c > 5:
                    break
                found_ids.add(i)
                this_group_set.add(i)
                print("--", i, round(s_tfidf * s_gensim,3), d[:100])
            # input("enter to continue...")
    group_sets.append(this_group_set)

from threading import Thread
t_list = list()
for idx, doc in enumerate(docs):
    # process_doc(docs_idx, idx, doc)
    t = Thread(target=process_doc, args=[docs_idx, idx, doc], daemon=True)
    t.start()
    t_list.append(t)
    if len(t_list) >= 8:
        for t_ in t_list:
            t_.join()
        t_list = list()
for t_ in t_list:
    t_.join()

compiled_groups = list()
for s in group_sets:
    this_group_added = False
    for c in compiled_groups:
        if isinstance(c, set):
            if len(c.intersection(s)) > 0:
                c.update(s)
                this_group_added = True
        if this_group_added:
            break
    if not this_group_added:
        compiled_groups.append(s)

    
print(f"found {sum([len(cg) for cg in compiled_groups])} docs, {len(compiled_groups)} groups")


def yield_nm(compiled_groups_, nm_list_):
    compiled_groups_.sort(key=lambda x: len(x), reverse=True)
    for cg in compiled_groups:
        for i in cg:
            nm = nm_list_[i]
            print(nm.header, nm.url)
            yield nm_list_[i]

from news_bmw_docx import convert_ng_nlp_iterable_to_docx, docx_out

convert_ng_nlp_iterable_to_docx(
    yield_nm(compiled_groups, nm_list),
    os.path.join(docx_out, "compiled.docx")
)
    