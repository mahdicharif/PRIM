The file generate_graph.sh enables to parse the XML file and produce the database of the articles and the graph.

Before launching the process, you must install the following libraries :

- mwparserfromhell
- networkdisk
--> clone the branch query++ and paste the following lines in your code :

sys.path.append("/path/to/networkdisk/")
import networkdisk as nd

- sentence_transformers (for the encoding part)