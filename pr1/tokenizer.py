# this program tokenize each file in the corpus and 
# save the tokens in the folder 'result'
# I use Porter Stemmer to stem the word
# and the stopword is represent as a empty line in the
# new file

from os import listdir
import re
import sys
import string
from bs4 import BeautifulSoup, Comment
import nltk
from time import time
from collections import Counter, defaultdict
import codecs



# Set default encoding to urf-8 instead of ascii
reload(sys)
sys.setdefaultencoding('utf-8')

#read the stop words from txt
stop_list =  open('stoplist.txt').read().split()

docidsfile = open('docids.txt','w')
termidsfile = open('termids.txt', 'w')
docindexfile = open('doc_index.txt','w')

# doc_dic is a dictionary that (key, vlue)=(docname, docid)
# global reverse_doc_dict

doc_dict = {}

# # term_dic is a dictioanry that (key, value)=(term, termid)
reverse_term_dict = {}

doc_index_dict = {}

global unique_term_count
global doc_count
doc_count = 0
unique_term_count = 0

# apply stemming with Porter algorithm
# def stem_words(terms):
# 	stemmer = nltk.stem.porter.PorterStemmer()
# 	terms = [stemmer.stem(word) for word in terms]
# 	return terms

def extract_document(directory):
	global doc_count
	global unique_term_count
	
	for fileitem in listdir(directory):
		if fileitem[0] != '.':
			# skip the hidden files
			# reverse_doc_dict[fileitem] = docindex
			# try:
			doc_count += 1
			doc_dict[doc_count] = fileitem
			docidsfile.write(str(doc_count)+'\t'+fileitem+'\n')
			try:
			# doc = codecs.open(directory+'/'+fileitem, 'r', encoding='utf-8')
				doc = open(directory+'/'+fileitem, 'r')
				# print doc
				# parse the document through beautifulsoup
				content = doc.read()
				# print content
				doc.close()
				content = content[content.find("<html"):]
				# .decode('utf-8', 'ignore')
				soup = BeautifulSoup(content.decode('utf-8', 'ignore'))
				# extract the comments in the documents
				[comment.extract() for comment in soup.findAll(text=lambda text:isinstance(text, Comment))]
				# extract the script and style tag in the documents
				extracttag = ['script', 'style']
				[tag.extract() for tag in soup.findAll(True) if tag.name in extracttag]
				extract_content(doc_count, soup.get_text(" "))
			except:
				print fileitem, doc_count, sys.exc_info()[0]

	docidsfile.close()
	termidsfile.close()

# split the documents into wordlist
# and convert the words into lowercase
# then stem the word
def extract_content(docid, content):
	# split the document with given regular expression
	doc_index = {}
	result = []
	global unique_term_count
	# extract the empty item in the wordlist  \w+(?:\.?\w+)
	# word_tokens = nltk.tokenize.regexp_tokenize(content,r'\w+(\.?\w+)*')
	tokenreg = re.compile(r"\w+(?:\.?\w+)*")
	word_tokens = re.findall(tokenreg, content)
	stemmer = nltk.stem.porter.PorterStemmer()
	pos = 1
	for w in word_tokens:
		lowerword = w.lower()
		if lowerword not in stop_list:
			# convert to lowercase
			word = stemmer.stem(lowerword)
			result.append(word)
			if word in reverse_term_dict:
				termid = reverse_term_dict[word]
			else:
				unique_term_count += 1
				reverse_term_dict[word] = unique_term_count
				termid = unique_term_count
				termidsfile.write(str(unique_term_count)+'\t'+word+'\n')
			if termid not in doc_index:
				doc_index[termid] = [pos]
			else:
				doc_index[termid].append(pos)
		else:
			# the stop words remian a position in the doc
			result.append('\n')
		pos += 1

	if len(doc_index) == 0:
		docindexfile.write(str(doc_count)+'\n')
	else:
		for termid, lop in doc_index.items():
			value = '\t'.join(str(p) for p in lop)
			docindexfile.write(str(doc_count)+'\t'+str(termid)+'\t'+value+'\n')

	return result


if __name__ == '__main__':
	starttime = time()

	extract_document(sys.argv[1])

	finishtime = time()
	print "total time is ", finishtime-starttime

	





		



	
