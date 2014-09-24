# read index, read the invert index linearly and
# loop up the offset in term_info.txt, 
# Examples
# $ ./read_index.py --doc clueweb12-0000tw-13-04988

# Listing for document: clueweb12-0000tw-13-04988
# DOCID: 1234
# Distinct terms: 25
# Total terms: 501

# $ ./read_index.py --term asparagus

# Listing for term: asparagus
# TERMID: 567
# Number of documents containing term: 315
# Term frequency in corpus: 567
# Inverted list offset: 1542

# $ ./read_index.py --term asparagus --doc clueweb12-0000tw-13-04988

# Inverted list for term: asparagus
# In document: clueweb12-0000tw-13-04988
# TERMID: 567
# DOCID: 1234
# Term frequency in document: 4
# Positions: 134, 155, 201, 233


import re
from os import listdir
import sys
import string
import argparse
import linecache


# invert doc dictionary uses docname as key and the docid as value
invert_doc_dic = {}

# invert term dictionary uses term as key and the termid as value
invert_term_dic = {}

docids = open('docids.txt','r').read().splitlines()
for line in docids:
	(docid, docname) = line.split()
	invert_doc_dic[docname] = int(docid)

termids = open('termids.txt','r').read().splitlines()
for line in termids:
	(termid, term) = line.split()
	# term_dic[int(termid)] = term
	invert_term_dic[term] = int(termid)

termindex = open('term_index.txt','r')


# read the document by docname and calculate the document word size
# if the specific document name is not found
# return an error information
def parsing_doc(docname):
	try:
		docid = invert_doc_dic[docname]
		docindex = open('doc_index.txt', 'r').read().splitlines()
		unique_token = 0
		total_token_count = 0
		for line in docindex:
			lis = line.split('\t')
			if int(lis[0]) == int(docid):
				if len(lis) > 1:
					unique_token += 1
					total_token_count += len(lis[2:])
		
		print "Listing for document:", docname
		print "DOCID:", docid
		print "Distinct terms:", unique_token
		print "Total terms:", total_token_count
	except:
		print "Didn't find such document:", docname

# find the TERMID by specific term
# return the term's information if find the term
# else return an error information
def parsing_term(term):
	try:
		termid = invert_term_dic[term]
		# terminfo = terminfo_dic[termid]
		terminfo = (linecache.getline('term_info.txt', int(termid))).split()
		print "List for term:", term
		print "TERMID:", termid
		print "Number of documents containing term:", terminfo[3]
		print "Term frequency in corpus:", terminfo[2]
		print "Inverted list offset:", terminfo[1]
	except:
		print "Didn't find such term:", term

def parsing_doc_term(docname, term):
	# term_info.txt contains the the term's basic information,
	# TERMID OFFSET TOTOAL_OCCURRENCE TOTAL_DOCUMENTS
	try:
		termid = invert_term_dic[term]
		docid = invert_doc_dic[docname]
		terminfos = (linecache.getline('term_info.txt', int(termid))).split()
		offset = int(terminfos[1])
		termindex.seek(offset)
		line = termindex.readline().split('\t')
		index = line[1:len(line)-1]

		isFirstElement = True
		lastdid = 0
		# get all the position of each document
		# term_dic = {}
		lop = []
		lastpos = 0
		for pair in index:
			(relate_did, relate_pos) = pair.split(':')
			curdid = int(relate_did) + int(lastdid)
			lastdid = curdid
			if curdid == docid:
				pos = int(relate_pos) + lastpos
				lastpos = pos
				lop.append(pos)
			elif curdid > docid:
				break
		print "Inverted list for term:", term
		print "In document:", docname
		print "TERMID:", termid
		print "DOCID:", docid
		print "Term frequency in document:", len(lop)
		print "Positions:", ", ".join(str(item) for item in lop)
	except:
		print "error occurs when finding document/term"





if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--doc', action='store', dest='doc_name')
	parser.add_argument('--term', action='store', dest='term_value')
	args = parser.parse_args()
	DOCNAME = args.doc_name
	TERMNAME = args.term_value
	if DOCNAME != None and TERMNAME != None:
		parsing_doc_term(DOCNAME, TERMNAME)
	elif DOCNAME == None and TERMNAME != None:
		parsing_term(TERMNAME)
	elif DOCNAME != None and TERMNAME == None:
		parsing_doc(DOCNAME)
	else:
		print "error occurs when parsing arguments"
