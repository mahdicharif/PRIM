

import xml.sax
import re
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer,util
import mwparserfromhell
import sqlite3
import json


# Cette fonction vient en complément des parsers, afin de parfaire certains parsing ne nettoyant pas le texte de façon optimale.

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

# Cette classe permet de récupérer les articles, leurs textes et liens internes (wikilinks)

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self._current_tag:
            self._buffer.append(content)

    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            if "disambiguation" not in self._values['text']:
                
                wiki = mwparserfromhell.parse(self._values['text'])

                tr = wiki.strip_code().strip()
                cleaned_text = cleanhtml(tr)
                cleaned_text = cleaned_text.split("\n")[0]
                
                wikilinks = [x.title for x in wiki.filter_wikilinks()]
                
                self._pages.append((self._values['title'], cleaned_text, wikilinks))
                
                
                
# Cette fonction reprend la classe précédente et effectue le processing sur tout un dump. Elle produit des fichiers pickle contenant les articles, leurs textes et les liens internes.
                

def process_data(path):
    conn = sqlite3.connect("/home/infres/mcharif/articles.db")
    c = conn.cursor()
    c.execute("CREATE TABLE Article(Name_article, Text_article, Links, Redirect)")
    conn.commit()
    conn.close()

    # Object for handling xml
    handler = WikiXmlHandler()

    # Parsing object
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    i = 0
    old = 0
    for line in bz2.BZ2File(path, 'r'):
        parser.feed(line)
        if i == 0:
            old = len(handler._pages)
            i += 1
        else:
            temp_old = len(handler._pages)

            if old != len(handler._pages):
                i += 1
                temp_old = len(handler._pages)

                if i % 100 == 0:

                    print("{} articles have been processed".format(i))

                    elements_insert = []

                    for p in handler._pages:

                        chosen_page = p
                        wikilinks = list(map(str, chosen_page[2]))
                        wikilinks = json.dumps(wikilinks).encode('utf8')

                        redir = chosen_page[1]
                        redirr = False

                        if "REDIRECT" in redir:
                            redirr = redir.replace("REDIRECT", "")
                        if "REDIRECT " in redir:
                            redirr = redir.replace("REDIRECT ", "")
                        if "redirect" in redir:
                            redirr = redir.replace("redirect", "")
                        if "redirect " in redir:
                            redirr = redir.replace("redirect ", "")

                        elements_insert.append((chosen_page[0], chosen_page[1], wikilinks, redirr))

                    u = 0
                    while True and u <= 3:
                        try:
                            conn = sqlite3.connect("/home/infres/mcharif/articles.db")
                        except:
                            u += 1
                            continue

                        c = conn.cursor()

                        c.executemany('INSERT INTO Article VALUES (?,?,?,?)', elements_insert)

                        conn.commit()
                        conn.close()

                        break

                    old = len(handler._pages)

                    elements_insert = None

                    # Object for handling xml
                    handler._pages = []
                    temp_old = 0

            old = temp_old

        
# Cette fonction prend en compte les redirections de chaque article et tente de récupérer le contenu de l'article vers lequel il est redirigé
        
def redir_handler(articles, texts, n = 10):
    for i,row in texts[:n].iterrows():
        
        if "REDIRECT" in row["Text_article"]:
            
            if "REDIRECT " in row["Text_article"]: # Cas où il y aurait un espace après REDIRECT
                target = row["Text_article"].replace("REDIRECT ","")
    
            else:
                target = row["Text_article"].replace("REDIRECT ","")
            
            if target in articles["Name_article"].tolist():
                
                text_ind = articles[articles["Name_article"] == target].index[0]
                row["Text_article"] = texts.loc[[text_ind]]["Text_article"].tolist()[0]
           
    return texts
                       

# Ces fonctions permettent de stocker et importer les embeddings des textes de chaque article
    
def store_data(data, name_output="articles_encoding.ann"):
    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    f = 768
    t = AnnoyIndex(f, 'angular')  # Length of item vector that will be indexed

    for i, row in data.iterrows():
        text_art = row["Text_article"]
        if len(text_art.split(" ")) > 10:
            try:

                v = model.encode(text_art)
                t.add_item(i, v)

            except:

                print(text_art)

    t.build(10)  # 10 trees
    t.save(name_output)

    print("Done")

def load_corpus(file_name):
    f = 768
    u = AnnoyIndex(f, 'angular')
    u.load(file_name)
    return u

def import_enc(file_name = "articles_encoding.ann"):
    model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
    embeddings = load_corpus(file_name)
    return(model, embeddings)

# Cette fonction permet de renvoyer la meilleure prédiction

def produce_prediction(query_text, model, embeddings, top_n = 3):
    query = model.encode(query_text)
    nearest = embeddings.get_nns_by_vector(query, top_n, include_distances = True)
    return nearest