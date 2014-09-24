import os
import sys
import re
import string
from bs4 import BeautifulSoup
import nltk
import argparse
import xml.etree.ElementTree as et
import linecache
import math
from time import time
import operator

class Rank:
	totalDocumentLen = 0
	avg_doc_len = 0
	avg_query_len = 0
	toatl_doc_num = 0
	vocabulary_size = 0
	total_query_len = 0
	total_doc_len = 0

	term_dict = {}
	doc_dict = {}
	query_dict = {}
	doc_index = {}
	doc_len = {}
	query_num = 0
	sorted_topic = {}
	term_index = {}
	term_info = {}
	doc_vector = {}

	def __init__(self):
		termidsfile = open('index/termids.txt', 'r')
		for term in termidsfile.read().splitlines():
			lis = term.split()
			self.term_dict[lis[1]] = lis[0]
		self.vocabulary_size = len(self.term_dict)
		termidsfile.close()

		docidsfile = open('index/docids.txt', 'r')
		for item in docidsfile.read().splitlines():
			lis = item.split()
			docid = lis[0]
			docname = lis[1]
			self.doc_dict[docid] = docname
			self.doc_len[docid] = 0
		self.total_doc_num = len(self.doc_dict)
		docidsfile.close()

		docindexfile = open('index/doc_index.txt', 'r')
		for line in docindexfile.read().splitlines():
			index = line.split()
			if len(index) > 0:
				docid = index[0]
				if len(index) > 1:
					termid = index[1]
					termcnt = len(index[2:])
					self.doc_index.setdefault(docid, {})[termid] = termcnt
					self.doc_len[docid] += termcnt
					self.total_doc_len += termcnt
				else:
					self.doc_index[docid] = 0
		docindexfile.close()
		self.avg_doc_len = self.total_doc_len / len(self.doc_dict) 

		terminfofile = open('index/term_info.txt', 'r')
		for line in terminfofile.read().splitlines():
			index = line.split()
			termid = index[0]
			# print index
			self.term_info[termid] = map(int, index[2:])
		terminfofile.close()

		## parse the xml , generate query dictionary
		topic_tree = et.parse('topics.xml')
		root = topic_tree.getroot()
		for item in root:
			if item.tag == 'topic':
				num = item.attrib.get('number')
				query = item.find('query').text
				querylis = self.token_query(query)
				self.query_dict[int(num)] = querylis
				self.total_query_len += len(querylis)
		self.avg_query_len = self.total_query_len / len(self.query_dict)

		self.query_num = len(self.query_dict)

		self.sorted_topic = sorted(list(map(int, self.query_dict.keys())))


	def token_query(self,query):
		## tokenize the query
		tokenreg = re.compile(r"\w+(?:\.?\w+)*")
		stemmer = nltk.stem.porter.PorterStemmer()
		stopwords = open('index/stoplist.txt', 'r')
		stoplist = []
		for word in stopwords.read().split('\n'):
			stoplist.append(word)
		tokens = re.findall(tokenreg, query)
		tokenized_query = ""
		for word in tokens:
			lower = word.lower()
			if lower not in stoplist:
				stemed = stemmer.stem(lower)
				if stemed in self.term_dict.keys():
					termid = self.term_dict[stemed]
					tokenized_query += termid + ' '
				else:
					tokenized_query += '0' + ' '
		return tokenized_query

	def query_tf_idf(self, query, termid):
		oktfval = self.query_oktf(query, termid)
		return oktfval*math.log(self.query_num*1.0/self.query_df(termid), 2)

	def query_oktf(self,topic, termid):
		query =self.query_dict[topic].split()
		tfvalue = query.count(str(termid))
		oktfvalue = float(tfvalue/(tfvalue+0.5+1.5*(len(query)/self.avg_query_len)))
		return oktfvalue

	# related doc means that at least one term in the query is in the document.
	# return a set of docid
	def get_related_docids(self, query):
		related_docs = set([])
		for (docid, td) in self.doc_index.items():
			if td != 0:
				lot = td.keys()
				if len(set(lot) & set(query)) > 0:
					related_docs.add(docid)
		return related_docs

	def get_query_contained_docs(self, query):
		docs = set([])
		for (docid, td) in self.doc_index.items():
			if td != 0:
				lot = td.keys()
				if set(lot) & set(query) == set(query):
					docs.add(docid)
		return docs

	def query_df(self, termid):
		cnt = 0
		for (k,v) in self.query_dict.items():
			query = v.split()
			if termid in query:
				cnt += 1
		return cnt



class TF_Rank(Rank):
	doc_vector = {}
	doc_norm = {}
	def __init__(self):
		Rank.__init__(self)
		# construct the document vector for each docuemnt
		# note that if the term is not in that doc,
		# then oktf(d,i)=0 so we only need to compute the termids
		# in the document. Other termid in the vector are set to 
		# a default value 0.
		for docid in self.doc_dict.keys():
			vector = [0.0]*self.vocabulary_size
			if self.doc_index[docid] != 0:
				for termid in self.doc_index[docid].keys():
					tf = self.doc_index[docid][termid]
					oktf = (tf*1.0)/(tf+0.5+1.5*(self.doc_len[docid]/self.avg_doc_len))
					vector[int(termid)-1] = oktf
			self.doc_vector[docid] = vector
			self.doc_norm[docid] = math.sqrt(sum(map(operator.mul, vector, vector)))

		# for each topic, we calculate its vector and the norm of the vector.
		# find all the related documents. calculate their score. Then do the
		# ranking.
		for topic in self.sorted_topic:
			score = {}
			query = self.query_dict[topic].split()
			rel_docs = sorted(self.get_related_docids(query))

			q_vector = {}
			for termid in query:
				q_vector[termid] = self.query_oktf(topic, termid)
			norm_q = math.sqrt(sum(map(operator.mul, q_vector.values(), q_vector.values())))

			for docid in rel_docs:
				norm_d = self.doc_norm[docid]
				dot_product = 0
				for termid in query:
					dot_product += self.doc_vector[docid][int(termid)-1]*q_vector[termid]
				doc_score = (dot_product*1.0)/(norm_d*norm_q)

				score[docid] = doc_score

			sorted_keys = sorted(score.iterkeys(), key=score.get, reverse=True)
			rank = 1
			for k in sorted_keys:
				print topic, '0', self.doc_dict[k], rank, score[k], 'run1'
				rank += 1
		self.doc_vector.clear()
		self.doc_norm.clear()

class TF_IDF_Rank(Rank):
	doc_vector = {}
	doc_norm = {}
	def __init__(self):
		Rank.__init__(self)
		# construct the document vector for each docuemnt
		# note that if the term is not in that doc,
		# then tfidf(d,i)=0 so we only need to compute the termids
		# in the document. Other termid in the vector are set to 
		# a default value 0.
		for docid in self.doc_dict.keys():
			vector = [0.0]*self.vocabulary_size
			if self.doc_index[docid] != 0:
				for termid in self.doc_index[docid].keys():
					tf = self.doc_index[docid][termid]
					oktf = (tf*1.0)/(tf+0.5+1.5*(self.doc_len[docid]/self.avg_doc_len))
					tfidf = oktf*math.log(self.total_doc_num*1.0/self.term_info[termid][1], 2)
					vector[int(termid)-1] = tfidf
			self.doc_vector[docid] = vector
			self.doc_norm[docid] = math.sqrt(sum(map(operator.mul, vector, vector)))

		# for each topic, we calculate its vector and the norm of the vector.
		# find all the related documents. calculate their score. Then do the
		# ranking.
		for topic in self.sorted_topic:
			score = {}
			query = self.query_dict[topic].split()
			# rel_docs is a list of docids. 
			# it contains all the docid that at least has one
			# term in the query.
			rel_docs = sorted(self.get_related_docids(query))
			q_vector = {}
			for termid in query:
				q_vector[termid] = self.query_tf_idf(topic, termid)

			norm_q = math.sqrt(sum(map(operator.mul, q_vector.values(), q_vector.values())))

			for docid in rel_docs:
				norm_d = self.doc_norm[docid]
				dot_product = 0
				for termid in query:
					dot_product += self.doc_vector[docid][int(termid)-1]*q_vector[termid]
				doc_score = (dot_product*1.0)/(norm_d*norm_q)
				score[docid] = doc_score

			sorted_keys = sorted(score.iterkeys(), key=score.get, reverse=True)
			rank = 1
			for k in sorted_keys:
				print topic, '0', self.doc_dict[k], rank, score[k], 'run1'
				rank += 1
		self.doc_vector.clear()
		self.doc_norm.clear()


class BM25_Rank(Rank):
	k1 = 1.2
	k2 = 1
	b = 0.9
	def __init__(self):
		Rank.__init__(self)
		for topic in self.sorted_topic:
			score = {}
			query = self.query_dict[topic].split()
			querylen = len(query)

			rel_docs = sorted(self.get_related_docids(query))

			if len(rel_docs) > 0:
				for docid in rel_docs:
					K = self.k1*1.0*(1 - self.b + (self.b * (self.doc_len[docid]/self.avg_doc_len)))
					doc_score = 0
					for termid in query:
						TF = 0
						DF = 0
						if termid != '0':
							if termid in self.doc_index[docid].keys():
								TF = self.doc_index[docid][termid]
							DF = self.term_info[termid][1]
						base = (self.total_doc_num+0.5)*1.0/(DF+0.5)
						if base != 0:
							tmp = math.log((self.total_doc_num+0.5)*1.0/(DF+0.5), 2)
							tmp *= (1+self.k1)*TF*1.0/(K+TF)
							tmp *= (1+self.k2)*TF*1.0/(self.k2+TF)
						doc_score += tmp
					score[docid] = doc_score
				sorted_keys = sorted(score.iterkeys(), key=score.get, reverse=True)
				rank = 1
				for k in sorted_keys:
					print topic, '0', self.doc_dict[k], rank, score[k], 'run1'
					rank += 1

class Laplace_Rank(Rank):
	def __init__(self):
		Rank.__init__(self)
		for topic in self.sorted_topic:
			score = {}
			query = self.query_dict[topic].split()
			rel_docs = sorted(self.get_related_docids(query))
			if len(rel_docs) > 0:
				for docid in rel_docs:
					doc_score = 0
					for termid in query:
						TF = 0
						if termid in self.doc_index[docid].keys():
							TF = self.doc_index[docid][termid]
						pd = (TF+1)*1.0/(self.doc_len[docid]+self.vocabulary_size)
						doc_score += math.log(pd, 2)
					score[docid] = doc_score
				sorted_keys = sorted(score.iterkeys(), key=score.get, reverse=True)
				rank = 1
				for k in sorted_keys:
					print topic, '0', self.doc_dict[k], rank, score[k], 'run1'
					rank += 1

class JM_Rank(Rank):
	lamb = 0.2
	def __init__(self):
		Rank.__init__(self)
		for topic in self.sorted_topic:
			score = {}
			query = self.query_dict[topic].split()

			rel_docs = sorted(self.get_related_docids(query))
			if len(rel_docs) > 0:
				for docid in rel_docs:
					doc_score = 0
					for termid in query:
						TF = 0
						tmp  = 0
						if termid != '0':
							if termid in self.doc_index[docid].keys():
								TF = self.doc_index[docid][termid]
							tmp = ((self.lamb*TF*1.0)/self.doc_len[docid])+(1-self.lamb)*1.0*self.term_info[termid][0]/self.total_doc_len
						if tmp != 0:
							doc_score += math.log(tmp*1.0, 2)
				
					score[docid] = doc_score
				# rank the document's score
				sorted_keys = sorted(score.iterkeys(), key=score.get, reverse=True)
				rank = 1
				for k in sorted_keys:
					print topic, '0', self.doc_dict[k], rank, score[k], 'run1'
					rank += 1


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--score', action='store', dest='function_name')
	args = parser.parse_args()
	function = args.function_name

	if function == 'TF':
		r = TF_Rank()
	if function == 'TF-IDF':
		r = TF_IDF_Rank()
	if function == 'BM25':
		r = BM25_Rank()
	if function == 'Laplace':
		r = Laplace_Rank()
	if function == 'JM':
		r = JM_Rank()
