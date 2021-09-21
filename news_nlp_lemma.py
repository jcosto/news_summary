"""
https://towardsdatascience.com/how-to-rank-text-content-by-semantic-similarity-4d2419a84c32
"""

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.corpus import stopwords

nltk.download('punkt')
stop_words = set(stopwords.words('english'))

class LemmaTokenizer:
    ignore_tokens = [',','.',';',':','"','``',"''",'`']
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [
            self.wnl.lemmatize(t)
            for t in word_tokenize(doc)
            if t not in self.ignore_tokens
        ]

tokenizer = LemmaTokenizer()
token_stop = tokenizer(' '.join(stop_words))