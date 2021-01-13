import sys, os
cdir = os.path.dirname(sys.argv[0])
sys.path.append(f"{cdir}/../")
import numpy as np

from sentence_transformers import SentenceTransformer,util
import sqlite3
import json

def convert_array(blob):
    return json.loads(blob)

def adapt_array(arr):
    return arr.tobytes()

def fact(x):
    dicti = {}
    for item in x:
        dicti[item[0]] = item[1]
    return dicti

fact2 = lambda y: [item[0] for item in y]

if len(sys.argv)>1:
	datapath = sys.argv[1]
else:
	datapath = "data"

dbpath = f"{datapath}/"


def encode_articles(path):
    sqlite3.register_converter('array', convert_array)
    con1 = sqlite3.connect(path + "art.db", detect_types=sqlite3.PARSE_DECLTYPES)
    con2 = sqlite3.connect(path + "embeddings.db", detect_types=sqlite3.PARSE_DECLTYPES)

    c1 = con1.cursor()
    c2 = con2.cursor()

    qu = "SELECT Name_article, Text_article FROM Article WHERE Redirect = 0"
    res = c1.execute(qu).fetchall()
    print("All articles loaded")

    c2.execute("CREATE TABLE IF NOT EXISTS Embeddings(Name text, Embedding array)")
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter('array', convert_array)
    con2.commit()

    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    print("model loaded")

    emb = []

    for i, item in enumerate(res):
        emb.append([res[i][0], model.encode(res[i][1])])  # I encode the sentence during this step

        if i % 1000 == 0 and i > 0:
            c2.executemany('INSERT INTO Embeddings VALUES (?,?)', emb)
            con2.commit()
            print("{} articles have been encoded".format(i))
            emb = []

    c2.executemany('INSERT INTO Embeddings VALUES (?,?)', emb)
    con2.commit()

    con1.close()
    con2.close()

encode_articles(dbpath)