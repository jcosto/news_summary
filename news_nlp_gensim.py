"""
https://towardsdatascience.com/how-to-rank-text-content-by-semantic-similarity-4d2419a84c32
"""

from re import subn
from gensim.utils import simple_preprocess
from news_nlp_lemma import stop_words

def preprocess(doc):
    doc = subn(r'<img[^<>]+(>|$)', " image_token ", doc)[0]
    # print(doc)
    doc = subn(r'<[^<>]+(>|$)', " ", doc)[0]
    doc = subn(r'\[img_assist[^]]*?\]', " ", doc)[0]
    doc = subn(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', " url_token ", doc)[0]
    return [
        token for token
        in simple_preprocess(doc, min_len=0, max_len=float("inf"))
        if token not in stop_words
    ]


import gensim.downloader as api
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from gensim.similarities import WordEmbeddingSimilarityIndex
from gensim.similarities import SparseTermSimilarityMatrix
from gensim.similarities import SoftCosineSimilarity

glove = api.load("glove-wiki-gigaword-50")
similarity_index = WordEmbeddingSimilarityIndex(glove)
from pprint import pprint
def get_doc_similarity_scores(query, corpus):
    """use preprocessed query and corpus"""
    # pprint([i[:15] for i in corpus + [query]])
    dictionary = Dictionary(corpus + [query])
    tfidf = TfidfModel(dictionary=dictionary)

    similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary, tfidf)

    query_tf = tfidf[dictionary.doc2bow(query)]

    index = SoftCosineSimilarity(
        tfidf[[dictionary.doc2bow(document) for document in corpus]],
        similarity_matrix
    )

    doc_similarity_scores = index[query_tf]

    return doc_similarity_scores
