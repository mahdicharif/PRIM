

import xml.sax
import re
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer,util
import mwparserfromhell


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

    # Object for handling xml
    handler = WikiXmlHandler()

    # Parsing object
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    i = 0
    old = 0
    for line in bz2.BZ2File(data_path, 'r'):
        parser.feed(line)
        if i == 0:
            old = len(handler._pages)
            i+=1
        else:
            temp_old = len(handler._pages)
            
            if old != len(handler._pages):
                i+=1
                temp_old = len(handler._pages)

                if  i % 100000 == 0:

                    print("{} articles have been processed".format(i))


                    article_name = []
                    text_article = []
                    wikil = [] # Cette liste contient tous les wikilinks/liens internes

                    for p in handler._pages:
                        chosen_page = p

                        article_name.append(chosen_page[0])

                        text_article.append(chosen_page[1])

                        wikil.append(chosen_page[2])

                    for k in range(len(wikil)):
                        wikil[k] = list(map(str, wikil[k]))

                    dict_articles = {"Name_article" : article_name, "Text_article" : text_article, "Links" : wikil}
                    links_nodes = pd.DataFrame(data = dict_articles) 

                    links_nodes.to_pickle("D:/XML/data/links_nodes_" + str(i/100000) + ".pkl")
                    
                    old = len(handler._pages)
                    
                    links_nodes, dict_articles, article_name, text_article, wikil = [None]*5


                    # Object for handling xml
                    handler._pages = []
                    temp_old = 0
                    
                    time.sleep(30)

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