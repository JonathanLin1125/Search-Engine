from HTMLParser import HTMLParser
from collections import defaultdict
import re
import math
import os
import json

INVERTED_FILE = "inverted_index.json"
LINK_FILE = "links.json"
NUM_RESULT = 10

class Parser(HTMLParser):
	master_word = defaultdict(dict)
	doc = ""
	ignore = ["script", "style"]
	ignoring = []
	skip = 0
	headerTag = ""
	headerWeight = 1

	def handle_starttag(self, tag, attrs):
		if tag in self.ignore:
			self.skip += 1
			self.ignoring.append(tag)
		if tag == 'h1':
			self.headerTag = tag
			self.headerWeight = 4
		elif tag == 'h2':
			self.headerTag = tag
			self.headerWeight = 3
		elif tag == 'h3':
			self.headerTag = tag
			self.headerWeight = 2

		if self.skip > 0:
			return

	def handle_endtag(self, tag):
		if tag in self.ignoring:
			self.skip -= 1
			self.ignoring.remove(tag)
		if tag == self.headerTag:
			self.headerTag = ""
			self.headerWeight = 1

	def handle_data(self, data):
		if self.skip > 0:
			return

		simple = re.sub('[^0-9a-zA-Z]+', ' ', data).lower()
		tokens = simple.split()

		for word in tokens:
			if len(word) > 2:
				if self.doc in self.master_word[word]:
					self.master_word[word][self.doc][0] += self.headerWeight
				else:
					self.master_word[word][self.doc] = [self.headerWeight]

"""Master link contains all words as the key, each word points to a dictionary with the docID as the key. Each docID points to a list
	containing the number of occurences of that word. We will append the tf-idf score to this list.

	master_word[word] = {docID: [num_occurences, tfidf]}
"""
def analyze_tfidf(master_word, num_docs):
	for (word, docs) in master_word.items():
		df = len(docs)
		idf = math.log10(float(num_docs)/float(df))

		for (doc_id, info_list) in docs.items():
			tf = info_list[0]
			weighted_tf = 1 + math.log10(tf)
			score = weighted_tf * idf
			master_word[word][doc_id].append(score)

"""For each word in the master_link, call parser to calculate the number of occurences.
	master_word[word] = {docID: [num_occurences]}
"""
def process_doc(parser, address):
	for addr in sorted(address):
		file = open("WEBPAGES_RAW/" + addr)
		parser.doc = addr
		text = file.read()
		data = text.decode('ascii', 'replace').replace(u'\ufffd', '_')
		parser.feed(data)
		file.close()

"""
	For each file in the bookkepping, add that to master_link.
	master_link[docID] = link_address
"""
def process_files():
	file = open("WEBPAGES_RAW/bookkeeping.tsv")
	line = file.readline()
	master_link = dict()

	while line:
		line_split = line.split()
		address = line_split[0]
		link = line_split[1]
		master_link[address] = link.strip()
		line = file.readline()
	
	file.close()
	return master_link

"""Saves the two dictionaries used to a Json file so that they can be retrieved in the future instead of being reprocessed. 
"""
def write_to_file(master_word, master_link):
	with open(INVERTED_FILE, 'w') as file:
		json.dump(dict(master_word), file)

	with open(LINK_FILE, 'w') as file2:
		json.dump(dict(master_link), file2)

"""Given a word, find all links that contain that word and append the cosine similarity score to a tuple. The list will
	consist of a list of tuples (link, consine similary score)
"""
def find_links(master_word, master_link, query_word, weight):
	sorted_docs = sorted(master_word[query_word].items(), key = lambda x: -x[1][1])
	top_docs = sorted_docs[:NUM_RESULT if len(sorted_docs) >= NUM_RESULT else len(sorted_docs)]

	top_links = []
	for doc in top_docs:
		top_links.append((master_link[doc[0]], (weight*doc[1][1])/(math.sqrt(doc[1][1] * doc[1][1]))))
	return top_links

"""Given a query phrase, returns a dictionary of each word's tf-idf
"""
def query_tfidf(master_word, num_docs, query_list, query_words_weight):
	for word in query_list:
		if word in master_word:
			df = len(master_word[word])
			idf = math.log10(float(num_docs)/float(df))

			weighted_tf = 1 + math.log10(query_list.count(word))
			score = weighted_tf * idf
			query_words_weight[word] = score

"""Given a query phrase, returns the top 10 links that are most relevant. 
"""
def query(master_word, master_link, query_phrase):
	query_list = query_phrase.strip().lower().split()

	#A list of tuples with all links retrieved and its corresponding cosine similarity score.
	#Total link_score = [(link, cosine similarity score), ...]
	total_link_score = []

	#A dictionary of all links and its (optinal) summed cosine similarity scores.
	total_link_dict = defaultdict(float)

	#Each query word's tf-idf score.
	query_words_weight = defaultdict(float)
	query_tfidf(master_word, len(master_link), query_list, query_words_weight)

	#For each word, return the links that contain the word and its cosine similarity score
	for word in query_list:
		if word in master_word:
			total_link_score += find_links(master_word, master_link, word, query_words_weight[word])

	#For links that show up more than once for different terms, add the score
	for link in total_link_score:
		total_link_dict[link[0]] += link[1]

	#Sort the retrieved links by how many time they appear, ties are broken by scores
	all_link = [link[0] for link in total_link_score]
	top_links = sorted(total_link_dict.items(), key = lambda x: (-all_link.count(x[0]), -x[1]))

	#return the top 10 results
	len_links = len(top_links)
	printed_links = []
	if len_links == 0:
		return printed_links
	else:
		count = 0
		index = 0
		while(count < len_links and count < NUM_RESULT):
			if(top_links[index][0] not in printed_links):
				count += 1
				printed_links.append(top_links[index][0])
			index += 1
		return printed_links
			
