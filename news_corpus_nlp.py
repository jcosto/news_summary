from pprint import pprint

from gensim.corpora.dictionary import Dictionary
from news_nlp import get_tfidf
from news_nlp_gensim import preprocess, get_doc_similarity_scores
from news import json_dir
import os
import json
from news import NewsMinimal

def get_docs_lists(json_dir_=json_dir, append_filter=None):
    if not append_filter:
        append_filter = lambda x : True
    urls = set()
    docs = list()
    nm_list = list()
    for f in os.listdir(json_dir_):
        fp = os.path.join(json_dir_, f)
        if os.path.isfile(fp) and '--nlp--applied' in fp:    
            print(f"loading {fp}")
            with open(fp, 'r', encoding='utf8') as fin:
                n_list = json.load(fin)
            for n in n_list:
                # pprint(n['ni'])
                if not append_filter(n['ni']):
                    continue
                url = n['ni']['url']
                if url in urls:
                    continue
                if len(n['ni']['summary']) == 0:
                    continue
                urls.add(url)
                doc = n['ni']['header'] + ' '+ n['ni']['summary']
                docs.append(doc)
                nm_list.append(NewsMinimal(
                    url, n['ni']['header'], n['ni']['summary'], doc, n['ni']['date']
                ))

    docs_idx = [[i,d] for i,d in enumerate(docs)]
    return docs, docs_idx, nm_list

import numpy as np
from sklearn.cluster import KMeans
from sklearn import svm
def get_threshold(d_scores):
    X = np.array(d_scores)
    print(X.shape)
    
    Kmean = KMeans(n_clusters=2)
    Kmean.fit(X)
    Y = Kmean.labels_
    print(Y.shape)

    clf = svm.SVC(kernel='linear')
    clf.fit(X, Y)
    w = clf.coef_[0]
    x_0 = -clf.intercept_[0]/w[0]
    print(f"found threshold {x_0}")

    return x_0

def get_doc_groups(docs, docs_idx):
    # DOCUMENT SIMILARITY
    
    d_scores = list()
    i_s_d__dict = dict()
    def process_doc(docs_idx, idx, doc):
        print(doc[:100])
        these_docs = [
            [i,d] for i,d in docs_idx if i != idx
            # and i not in found_ids
        ]
        
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
            # if s_tfidf * s_gensim > 0.25341969 # parang ok. max 5 content + header, svm from kmeans
            # if s_tfidf * s_gensim > 0.34303545 
        ]
        i_s_d.sort(reverse=True, key=lambda x: x[1] * x[2])
        if i_s_d:
            print(doc[:100])
            c = 0
            for i, s_tfidf, s_gensim, d in i_s_d:
                c += 1
                if c > 5:
                    break
                d_scores.append([s_tfidf, s_gensim])
                # print("--", i, round(s_tfidf * s_gensim,3), d[:100])
            # input("enter to continue...")
        i_s_d__dict[idx] = i_s_d

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


    threshold = get_threshold(d_scores)

    group_sets = list()
    for idx in i_s_d__dict:
        i_s_d = [
            [i, s1, s2, d]
            for i, s1, s2, d in i_s_d__dict[idx]
            if s1 * s2 > threshold
        ]
        this_group = set([idx])
        if i_s_d:
            print(doc[:100])
            c = 0
            for i, s_tfidf, s_gensim, d in i_s_d:
                c += 1
                if c > 5:
                    break
                this_group.add(i)
                print("--", i, round(s_tfidf * s_gensim,3), d[:100])
        group_sets.append(this_group)


    compiled_groups = list()
    for s in group_sets:
        this_group_added = False
        for c in compiled_groups:
            if isinstance(c, set):
                if len(c.intersection(s)) > 0:
                    c.update(s)
                    this_group_added = True
                    break
        if not this_group_added:
            compiled_groups.append(s)
    
    print(f"found {sum([len(cg) for cg in compiled_groups])} docs, {len(compiled_groups)} groups")
    return compiled_groups


def yield_nm(compiled_groups_, nm_list_):
    compiled_groups_.sort(key=lambda x: len(x), reverse=True)
    for cg in compiled_groups_:
        for i in cg:
            nm = nm_list_[i]
            print(nm.header, nm.url)
            yield nm_list_[i]

from news_bmw_docx import convert_ng_nlp_iterable_to_docx, docx_out

def process_grouped_sorted(json_dir_=json_dir, docx_out_=docx_out, append_filter=None):
    docs, docs_idx, nm_list = get_docs_lists(json_dir_=json_dir_, append_filter=append_filter)
    compiled_groups = get_doc_groups(docs, docs_idx)
    convert_ng_nlp_iterable_to_docx(
        yield_nm(compiled_groups, nm_list),
        os.path.join(docx_out_, "compiled.docx")
    )

if __name__ == "__main__":
    process_grouped_sorted(json_dir_=json_dir, docx_out_=docx_out)
    