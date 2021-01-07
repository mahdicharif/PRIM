from sentence_transformers import SentenceTransformer,util
import sqlite3
import numpy as np

def adapt_array(arr):

    return arr.tobytes()

def convert_array(blob):

    return np.frombuffer(blob)

# Register the new adapters

def store_data(path):

    con = sqlite3.connect(path + "articles.db")
    cu = con.cursor()
    qu = "SELECT Name_article, Text_article FROM Article WHERE Redirect = 0"
    res = cu.execute(qu).fetchall()
    con.close()

    print("data loaded")
    print("the length of the data is {}".format(len(res)))
    conn = sqlite3.connect(path + "embeddings.db", detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()
    c.execute("CREATE TABLE Embeddings(Name text, Embedding array)")
    sqlite3.register_adapter(np.ndarray, adapt_array)
    sqlite3.register_converter('array', convert_array)
    conn.commit()
    conn.close()

    print("table created")

    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    print("model loaded")

    conn = sqlite3.connect(path + "embeddings.db", detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()

    emb = []

    for i in range(len(res)):

        emb.append([res[i][0], model.encode(res[i][1])]) # I encode the sentence during this step

        if i % 100 == 0 and i > 0:
            c.executemany('INSERT INTO Embeddings VALUES (?,?)', emb)
            conn.commit()
            print("{} articles have been encoded".format(len(emb)))
            emb = []



    conn.close()

store_data("/media/ir610/users/mcharif/")
