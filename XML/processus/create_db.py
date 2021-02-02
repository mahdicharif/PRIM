#! /usr/bin/python3
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
sys.path.append(f"{cdir}/../")
import networkdisk as nd

cleanr = re.compile('<.*?>')
stripws = re.compile("\s+")
txt_limit = 202
commit_factor = 10**2

def cleanhtml(raw_html):
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = " ".join(filter(bool, stripws.split(cleantext)[:txt_limit]))
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
        if name == "page":
            self._redirect = False

        if name in ('title', 'text', "redirect"):
            self._current_tag = name
            self._buffer = []
            self._attrs = attrs

    def endElement(self, name):
        """Closing tag of element"""
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)

        if name == 'page':
            wiki = mwparserfromhell.parse(self._values['text'])
            tr = wiki.strip_code().strip()
            cleaned_text = cleanhtml(tr)
            wikilinks = [str(x.title) for x in wiki.filter_wikilinks()]
            self._pages.append((self._values['title'], cleaned_text, wikilinks, self._redirect))
        if name == "redirect":
            self._redirect = self._attrs.getValue("title")

def create_nd_graph(path):
    G = nd.sqlite.DiGraph(db=f"{path}wiki.db", sql_logger=True, insert_schema=True)
    handler = WikiXmlHandler()
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    i = 0
    def load_graph():
        G.add_edges_from([(page[0], link) for page in handler._pages for link in page[2]])
        G.add_nodes_from([(page[0], {"content":page[1], "is_redirect":page[3]}) for page in handler._pages])
    print("starting parser")
    for line in bz2.BZ2File(path + "wiki.xml.bz2", 'r'):
        parser.feed(line)
        if len(handler._pages) > commit_factor:
            i+= 1
            print(f"Commiting to nd Graph: {i*commit_factor} pages commited) ...", end="")
            load_graph()
            print("... done")
            handler._pages = []
    load_graph()

datapath = sys.argv[1] if len(sys.argv) > 1 else "data"
dbpath = f"{datapath}/"
create_nd_graph(dbpath)
