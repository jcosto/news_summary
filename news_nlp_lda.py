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

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
import string
stopwords = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(doc):
    stopwords_removal = ' '.join([i for i in doc.lower().split() if i not in stopwords])
    punc_removal = ''.join([ch for ch in stopwords_removal if ch not in exclude])
    normalized = " ".join([lemma.lemmatize(word) for word in punc_removal.split()])
    return normalized

final_doc = [clean(doc).split() for doc in docs]
print(docs[0])
print(final_doc[0])

from gensim import corpora

dictionary = corpora.Dictionary(final_doc)

DT_matrix = [dictionary.doc2bow(doc) for doc in final_doc]
import gensim
Lda_object = gensim.models.ldamodel.LdaModel

lda_model_1 = Lda_object(DT_matrix, num_topics=5, id2word = dictionary)

for i in lda_model_1.show_topics(num_topics=5, num_words=5):
    print(i)
