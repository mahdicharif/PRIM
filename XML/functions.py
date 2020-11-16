

import xml.sax
import re
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer,util
import mwparserfromhell

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


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


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

def produce_prediction(query_text, model, embeddings, top_n = 3):
    query = model.encode(query_text)
    nearest = embeddings.get_nns_by_vector(query, top_n, include_distances = True)
    return nearest