import sys, os
cdir = os.path.dirname(sys.argv[0])
sys.path.append(f"{cdir}/../")
import sqlite3
import bz2
import xml.sax
import re
import mwparserfromhell
import json
import time


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


# This class enables to retrieve the articles, their texts and internal links (wikilinks)

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

            wiki = mwparserfromhell.parse(self._values['text'])

            tr = wiki.strip_code().strip()
            cleaned_text = cleanhtml(tr)
            cleaned_text = cleaned_text.split("\n")[0]

            wikilinks = [x.title for x in wiki.filter_wikilinks()]

            self._pages.append((self._values['title'], cleaned_text, wikilinks))


def process_data(path):
    conn = sqlite3.connect(path + "art.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS Article(Name_article text, Text_article text, Links array, Redirect)")
    conn.commit()
    conn.close()

    # Object for handling xml
    handler = WikiXmlHandler()

    # Parsing object
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    i = 0
    old = 0
    for line in bz2.BZ2File(path + "enwiki-20201201-pages-articles.xml.bz2", 'r'):
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
                            conn = sqlite3.connect(path + "art.db")
                        except:
                            u += 1
                            print("Bug. Retrying.")
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


if len(sys.argv)>1:
	datapath = sys.argv[1]
else:
	datapath = "data"

dbpath = f"{datapath}/"


process_data(dbpath)
