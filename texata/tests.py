# -*- coding: utf-8 -*-
"""
@author: Álvaro Barbero Jiménez
"""

import dataloader
import text
import semantic
import clustering
import numpy as np

#corpus = text.PostsCorpus([
#        "robotics.stackexchange.com"
#    ])
    
#modelsdir = '../../models/'
#modelfiles = ['polyglot-en.pkl', 'word2vec-cisco.pkl', 'word2vec-stackexchange.pkl']
#modelfiles = ['polyglot-en.pkl', 'word2vec-stackexchange.pkl']
#modelfiles = ['word2vec-stackexchange.pkl']
#embeddings = [semantic.loadembedding(modelsdir + modelfile) for modelfile in modelfiles]
#    
#mapper = SemanticMapper(embeddings, embeddingbyall)
#    
#vectors, tags = zip(*[(mapper.map(item[0]),item[1]) for item in corpus.itertagged()])
#score = intertagscore(vectors, tags)
    
#res = corpus.search("arm")
#    
#question = ("I could swear that it was working for a while. I got back to my desk, tried it again, and it's no longer working. Could I have fried the NO pins on both sides? This is a DPDT relay. Everything works normally on the NC pins. I have never applied more than 5V. I do hear the relay click when I apply 5V to the coil. But when I measure voltage on the NO pins, I get 0V. Has anyone else seen this? I have two of these relays and I can't seem to get voltage on the NO pins with either relay. I should clarify that I'm expecting the same 5V power source to power both the coil and the common pins. If the NC pins work then I don't see why the NO pins shouldn't. In both cases the 5V is shared between the coil and any load attached to the NC/NO pins. I did try driving the entire circuit off a 9V power supply, but that did not change the results (and that does contradict my earlier statement that I've never applied more than 5V to this relay). My circuit is based on Charles Platt's \"Make: Electronics\", p. 59. Here's a pic of the schematic I am following, except that I am using a 5V relay and a 5V power supply (USB port) and I am using piezo buzzers without resistors instead of LEDs. ")
#              
#mapper = semantic.SemanticMapper(embeddings, semantic.embeddingbyall)
#
#corpus = text.PostsCorpus(["robotics.stackexchange.com"])
#neighbors = clustering.nearestneighbors(question, corpus, mapper)
    
#
#
#
#mapper = semantic.SemanticMapper(embeddings, semantic.embeddingbyall)
#vectors, tags = zip(*[(mapper.map(item[0]),item[1]) for item in corpus.itertagged()])
#
#score = clustering.intertagscore(vectors, tags, similarity=clustering.cosinesimilarity)
#print score
#
## Optimize score
#w = clustering.finetuneweightstags(vectors, tags)
#score = clustering.intertagscore(vectors, tags, similarity=clustering.weightedcosinesimilarity, weights=w)
#print score
    
ciscoembedding = semantic.loadembedding('../../models/word2vec-cisco.pkl')
wikipediaembedding = semantic.loadembedding('../../models/polyglot-en.pkl')
ciscowords = set(ciscoembedding.words)
wikipediawords = set(wikipediaembedding.words)
ciscowords = {word for word in ciscowords if word not in wikipediawords}
#ciscovectors = np.array([ciscowords[word] for word in ciscowords])