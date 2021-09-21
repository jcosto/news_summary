"""
todo:
word formatting from python (python-docx)
tf-idf and semantic similarity on summary sentences to prevent repeating article header
ph vs ROW news: how to get geographic source of data from article?
tf-idf/semantic similarity to rank news based on duplication among news sources

finished handlers
https://www.reuters.com/business/finance/
https://www.cnbc.com/finance/

todo handlers
https://www.bworldonline.com/category/top-stories/
https://www.bworldonline.com/category/banking-finance/
https://www.bworldonline.com/category/economy/
https://edition.cnn.com/business

https://business.inquirer.net/
https://www.gmanetwork.com/news/money/

maybe todo
https://www.manilatimes.net/business
"""

import requests
import datetime
API_KEY = '1579ff1d26fe46239ffdf2fc2a3ee721'
a = requests.get(
    # 'https://newsapi.org/v2/everything', # The category param is not currently supported on the /everything endpoint
    'https://newsapi.org/v2/top-headlines',
    params = {
        "apiKey": API_KEY,
        # "domains": "bworldonline.com",
        "category": "business",
        "from": (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()[:10],
        "country": "ph"
    }
).json()

import json
with open('test.json', 'w') as fout:
    json.dump(a, fout, sort_keys=True, indent=4)
