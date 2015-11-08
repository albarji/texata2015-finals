# -*- coding: utf-8 -*-
"""

Utilities for processing texts

@author: Álvaro Barbero Jiménez
"""

import nltk
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

# Connect to ElasticSearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

class Text(object):
    """Class representing a tokenized and cleaned text"""
    def __init__(self, inputtxt):
        # Split text in tokens
        self._tokens = nltk.word_tokenize(inputtxt)

    def __str__(self):
        return str(self._tokens)
        
    def __repr__(self):
        return self._tokens.__repr__()
        
    def __iter__(self):
        for token in self._tokens:
            yield token
            
    def __len__(self):
        return(len(self._tokens))
        
class PostsCorpus():
    """Class representing a corpus of posts and comments"""
    
    def __init__(self, esindexes):
        """Prepare a new corpus for querying.
        
        Inputs:
            esindexes: list of names of ElasticSearch indexes with the data
        """
        self._esindexes = esindexes
        
    def allposts(self):
        """Generator of all texts in the corpus"""
        return scan(es, index=','.join(self._esindexes), 
                    fields=["text","comments.text"], request_timeout=30)
        
    def textsbygroups(self):
        """Generator of texts grouped by post and its comments"""
        return TextsByGroupsIterator(self)
        
    def alltaggedposts(self):
        """Generator of posts and tags, for those posts with tags"""
        return scan(es, index=','.join(self._esindexes), 
                    fields=["text","tags"], request_timeout=30)
        
    def __iter__(self):
        return AllTextsIterator(self)
        
    def itertagged(self):
        return TextsWithTagsIterator(self)
        
    def search(self, text, size=100):
        """Returns a number of search results for a given text.
        
        Only performs the search in the opening texts, not in the comments"""
        queryresult = es.search(index=self._esindexes, size=size, body={
            "query":{"match":{"text":text}}, 
            "fields": "text"
            })
        return [Text(hit['fields']["text"][0]) for hit in queryresult['hits']['hits']]
        
    
class AllTextsIterator():
    """Class for iterating over all texts in a corpus"""
    def __init__(self, corpus):
        self._corpus = corpus
        self._generator = corpus.allposts()
        self._buffer = []
        
    def next(self):
        # If contents in the buffer, produce one
        if len(self._buffer) == 0:
            # Get the opening text and all the comments
            resultfields = self._generator.next()['fields']
            self._buffer.append(resultfields['text'][0])
            if 'comments.text' in resultfields:
                self._buffer.extend(resultfields['comments.text'])
        # Return next text
        return Text(self._buffer.pop())

    def __iter__(self):
        return self
        
class TextsByGroupsIterator():
    """Class for iterating over all text, grouped by post"""
    def __init__(self, corpus):
        self._corpus = corpus
        self._generator = corpus.allposts()
        
    def next(self):
        # Get the opening text and all the comments
        resultfields = self._generator.next()['fields']
        texts = [resultfields['text'][0]]
        if 'comments.text' in resultfields:
            texts.extend(resultfields['comments.text'])
        # Return list with all captured texts
        return [Text(text) for text in texts]

    def __iter__(self):
        return self
        
class TextsWithTagsIterator():
    """Class for iterating over all texts that include tags"""
    def __init__(self, corpus):
        self._generator = corpus.alltaggedposts()
        
    def next(self):
        # Get texts until one with tags appears
        tags = None
        while not tags:
            resultfields = self._generator.next()['fields']
            if 'tags' in resultfields and len(resultfields['tags']) > 0:
                text = resultfields['text'][0]
                tags = resultfields['tags']
        # Return list with all captured texts
        return (Text(text), tags)

    def __iter__(self):
        return self