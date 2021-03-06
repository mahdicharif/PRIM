#! /bin/bash

#pdir: the program dir (where to find subscripts)
pdir="$(dirname $0)"
pdir="${pdir:-.}"
pdir="${pdir%/}"
wiki_url="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"

#option flags (c.f. help)
clean=true
force=false
interactive=false
master=false
while getopts "Cfhis" opt
do
	case $opt in
		C) clean=false;;
		f) force=true;;
		h) echo "Usage: $0 [-Cfhis] [directory]"
			echo
			echo " -C  do not clean downloaded files after import"
			echo " -f  force import (overwrite previously imported DBLP data)."
			echo " -h  show this help and exit. "
			echo " -i  load the graph in interactive ipython, after import."
			echo " -s  save the graph schema in master table."
			exit 0;;
		i) interactive=true;;
		s) master=true;;
	esac
done
shift $(($OPTIND-1))

#dirpath: the target directory (where to download and import)
dirpath="${1:-.}"
[ ! -d "$dirpath" ] && echo "$dirpath: not a directory" >&2 && exit 1
dirpath="${dirpath%/}/$(date "+%y%m%d")"

#Download and import
if $force || [ ! -f "$dirpath/art.db" ]
then
	echo "Caution, the script will download large files"
	mkdir -p "$dirpath"
	if [ ! -f "$dirpath/wiki.xml.bz2" ]; then
		if ! wget -O "$dirpath/wiki.xml.bz2" "$wiki_url"; then
			exit 1;
		fi
	fi
	echo "Parsing of Wikipedia"
	python3 "$pdir/create_db.py" "$dirpath"
	echo "Creating the embeddings"
	python3 "$pdir/encode.py" "$dirpath"
	echo "Creating the graph"
	pyhton3 "$pdir/graph.py" "$dirpath"

else
	echo "Wikipedia graph found in $dirpath/digraph.db (use -f to overwrite)."
fi


#Launch interactive mode
if $interactive
then
	ipython3 -c "import networkdisk as nd; $pyopengraph; print('Play with the Wikipedia graph G.')" -i
else
	echo "Within Python, use:"
	echo ">>> import networkdisk as nd"
	echo ">>> $pyopengraph"
fi

