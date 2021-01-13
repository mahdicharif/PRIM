import json
import sqlite3
import time
import sys, os
cdir = os.path.dirname(sys.argv[0])
sys.path.append(f"{cdir}/../")

if len(sys.argv)>1:
	datapath = sys.argv[1]
else:
	datapath = "data"

dbpath = f"{datapath}/"

sys.path.append(dbpath + "networkdisk/")
import networkdisk as nd


def convert_array(blob):
    return json.loads(blob)


def generate_graph(path):

    start = time.process_time()

    G = nd.sqlite.DiGraph(db = path + "digraph.db", nom="A", insert_schema=True, sql_logger=True)

    print("The graph has been created")

    sqlite3.register_converter('array', convert_array)
    con = sqlite3.connect(path + "art.db", detect_types=sqlite3.PARSE_DECLTYPES)

    cu = con.cursor()
    qu = "SELECT Name_article, Links FROM Article"
    pe = list(cu.execute(qu))

    pe = [(node1, element) for node1, l in pe for element in l]
    length = len(pe)

    print("The data has been imported after {} seconds".format(time.process_time() - start))
    print("Its length is {}".format(length))

    ind = 80000000
    next_i = 0
    
    while next_i < length: # length of the whole db

        print("beginning to insert the next 80 000 000 edges")

        start = time.process_time()
        
        dat = pe[next_i:ind]

        print("data loaded")

        G.add_edges_from(dat)

        print("{} edges have been added".format(ind))
        print("after {} seconds".format(time.process_time() - start))
        print("\n")

        ind += 80000000
        next_i += 80000000
        dat = None

    G.helper.db.close()
    con.close()


generate_graph(dbpath)