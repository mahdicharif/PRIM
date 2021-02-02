#! /usr/bin/python3
import sys, os
cdir = os.path.dirname(sys.argv[0])
sys.path.append(f"{cdir}/../")
import sqlite3
import bz2
# import xml.sax
from lxml import etree
import re
import mwparserfromhell
import time
import json
import time
sys.path.append(f"{cdir}/../")
import networkdisk as nd
import collections
cleanr = re.compile('<.*?>')
stripws = re.compile("\s+")
extract_word = re.compile("\s(\w+)")
extract_wikilink = re.compile("\[\[([^|\]]*)")
txt_limit = 202
commit_factor = 10**3 
ns = "{http://www.mediawiki.org/xml/export-0.10/}"

def cleanhtml(raw_html):
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = " ".join(filter(bool, stripws.split(cleantext)[:txt_limit]))
    return cleantext

page_class = collections.namedtuple("page_class", ("title", "links", "redirect", "content"))

def create_nd_graph(path):
    G = nd.sqlite.DiGraph(db=f"{path}wiki.db", sql_logger=False, insert_schema=True)
    i = 0
    Tinit = T = time.time_ns()
    fsize = os.stat(f"{path}wiki.xml.bz2").st_size
    f = bz2.open(f"{path}wiki.xml.bz2")
    context = etree.iterparse(f, tag=f"{ns}page") # will stop at each tag page
    def load_graph(pages):
        T2 = time.time_ns()
        G.add_edges_from([(page.title, link) for page in pages for link in page.links])
        T3 = time.time_ns()
        G.add_nodes_from([(page.title, {"content":page.content, "is_redirect":page.redirect}) for page in pages])
        T4 = time.time_ns()
        return T2, T3, T4
    pages = []
    for _, page in context:
        T0 = time.time_ns()
        title = page.find(f"{ns}title").text
        content = page.find(f"{ns}revision/{ns}text").text
        it = extract_word.finditer(content)
        clear_content = ""
        for j, a in enumerate(it):
            clear_content += " "+a.groups()[0]
            if j > 200:
                break
        links = extract_wikilink.findall(content)
        redirect = page.find(f"{ns}redirect")
        if redirect is not None:
            redirect = redirect.attrib["title"]
        pages.append(page_class(title=title, links=links, content=content, redirect=redirect))
        if len(pages) > commit_factor:
            T2, T3, T4 = load_graph(pages)
            if i:
                print("\033[A"*10)
            i+= 1
            print(f"{commit_factor*i} pages inserted")
            print(f"Parsing:\t\t{(T2-T)/10**6:.2f}ms")
            print(f"Total nd:\t\t{(T4-T2)/10**6:.2f}ms")
            print(f"\tAdd edges:\t{(T3-T2)/10**6:.2f}ms")
            print(f"\tAdd nodes:\t{(T4-T3)/10**6:.2f}ms")
            print(f"Total: {(i*commit_factor*10**9)/(T4-Tinit):.2f} Pages/s")
            print(f"Last loop: {commit_factor*10**9/(T4-T):.2f} Page/s") 
            print(f"File cursor: {1000*f.tell()/fsize:.2f}‰ ")
            print(f"Time remaining {((T4 - Tinit)*fsize/f.tell())/(60*10**9):0.1f} minutes")
            T = T4
            pages = []
        page.clear() # free memory
    load_graph()
    G.helper.db.close()

datapath = sys.argv[1] if len(sys.argv) > 1 else "data"
dbpath = f"{datapath}/"
create_nd_graph(dbpath)
