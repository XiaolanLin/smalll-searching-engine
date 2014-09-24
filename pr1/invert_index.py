# construct the invert index for the corpus
# the term_index.txt file is construct by the following rule
# TERMID DOCID:POS DOCID:POS
import re
import sys
import string
from time import time
import collections
import resource

starttime = time()

index_file = open('doc_index.txt', 'r')



# invert index dictionary 
# key = termid
# value = {} which in the value dictionary
# kye = docid , value = list of positions
invert_index = {}
for item in index_file.read().splitlines():
	lis = item.split()
	if len(lis) > 1:
		termid = int(lis[1])
		docid = lis[0]
		invert_index.setdefault(termid, {})[docid] = lis[2:]

# for each termid, print their related docids and the position of 
# the term in the particular doc
# for each termid as the key in the invert_index dictionary
# there is a dictionary docidx which contains all the doc info that
# contianining that term
# sorted_termid = sorted(map(int, invert_index.keys()))
termindexfile = open('term_index.txt','w')
terminfofile = open('term_info.txt','w')
term_size = len(invert_index)

for sid in range(1, term_size+1):
	termid = sid
	docidx = invert_index[termid]
	offset = termindexfile.tell()
	termindexfile.write(str(termid)+'\t')
	lastkey = 0

	sorted_keys = sorted(list(map(int, docidx.keys())))
	doc_num = len(sorted_keys)
	occurs = 0
	for k in sorted_keys:
		v = docidx[str(k)]
		occurs += len(v)
		re_key = k-lastkey
		lastkey = k
		termindexfile.write(str(re_key)+":"+str(v[0])+'\t')
		lastpos = int(v[0])
		if len(v) > 1:
			for pos in v[1:]:
				repos = int(pos) - lastpos
				termindexfile.write('0:'+str(repos)+'\t')
				lastpos = int(pos)
	termindexfile.write('\n')
	terminfofile.write(str(termid)+'\t'+str(offset)+'\t'+str(occurs)+'\t'+str(doc_num)+'\n')

termindexfile.close()
terminfofile.close()

finishtime = time()

print "total memory usage:", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

print "total running time is ", finishtime-starttime, "seconds"

