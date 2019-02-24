#!/usr/bin/env python2
from flask import Flask
from flask import request
from flask import render_template
from forms import SearchForm
import json
import os

import project3

INVERTED_FILE = "inverted_index.json"
LINK_FILE = "links.json"

app = Flask(__name__)

def load_index():
    global master_link
    global master_word
    if(os.path.isfile(INVERTED_FILE) and os.path.isfile(LINK_FILE)):
    	inverted_file = open(INVERTED_FILE)
    	master_word = json.loads(inverted_file.read())
    	link_file = open(LINK_FILE)
    	master_link = json.loads(link_file.read())
    	inverted_file.close()
    	link_file.close()

    else:
    	parser = project3.Parser()
    	master_link = project3.process_files()
    	project3.process_doc(parser, master_link.keys())
    	project3.analyze_tfidf(parser.master_word, len(master_link))
    	project3.write_to_file(parser.master_word, master_link)
        master_word = parser.master_word

@app.route('/')
def home():
    form = SearchForm()
    return render_template('home.html', form=form)

@app.route('/search', methods=('get', 'post'))
def search():
    query = request.form['search']
    results = project3.query(master_word, master_link, query)
    return render_template("results.html", results=results)

if __name__ == "__main__":
    print "starting app"
    load_index()
    print "loaded index"
    app.run()
