# -*- coding: utf-8 -*-
"""
Module for clustering vectors.

@author: Álvaro Barbero Jiménez
"""
import numpy as np
from scipy import spatial, stats
from sklearn.grid_search import RandomizedSearchCV

def euclideansimilarity(a, b):
    """Similarity of vectors computed as inverse euclidean distance"""
    return -np.linalg.norm(a-b)
    
def cosinesimilarity(a, b):
    """Cosine similarity between two vectors"""
    return 1 - spatial.distance.cosine(a, b)
    
def weightedcosinesimilarity(a, b, w):
    """Weighted version of cosine similarity"""
    wa = np.array(a) * np.array(w)
    wb = np.array(b) * np.array(w)
    return cosinesimilarity(wa, wb)

def intergroupscore(vectorgroups, similarity=euclideansimilarity):
    """Computes a clustering score based on groups.
    
    Counts the similarity between vectors in the same group with positive
    score, and the distance between vectors in different groups with positive
    score.
    
    Inputs:
        vectorgroups: list of groups of vectors
        similarity: similarity function receiving two vectors
        
    Outputs:
        clustering score
    """
    
    score = 0
    # Positive scoring: vectors in the same group
    for group in vectorgroups:
        for index1, vector1 in enumerate(group):
            for index2, vector2 in enumerate(group):
                if index2 > index1:
                    score += similarity(vector1, vector2)
                
    # Negative score: vectors in different groups
    for idx1, group1 in enumerate(vectorgroups):
        for idx2, group2 in enumerate(vectorgroups):
            if idx2 > idx1:
                for vector1 in group1:
                    for vector2 in group2:
                        score -= similarity(vector1, vector2)    
                        
    # Normalize by the number of comparisons
    n = np.sum([len(group) for group in vectorgroups])
    return score / (n*(n-1)/2)
    
def intertagscore(vectors, tags, similarity=euclideansimilarity, weights = None):
    """Computes a clustering score based on tags.
    
    Similar to intergroup score but each vector may have multiple tags.
    Similarity within texts of the same tag is counted positively,
    while similarity within texts of different tags is counted negatively.
    
    Inputs:
        vectors: list of vectors
        tags: list of tags for each vector
        similarity: similarity function receiving two vectors
        
    Outputs:
        clustering score
    """
    
    score = 0
    
    for index1, couple1 in enumerate(zip(vectors,tags)):
        vector1, tags1 = couple1
        for index2, couple2 in enumerate(zip(vectors,tags)):
            vector2, tags2 = couple2
            if index2 > index1:
                # Positive if any one tag coincides
                intersect = [tag for tag in tags1 if tag in tags2]
                if len(intersect) > 0:
                    if weights:
                        score += similarity(vector1, vector2, weights)
                    else:
                        score += similarity(vector1, vector2)
                else:
                    # Negative if there is no tag coincidence
                    if weights:
                        score -= similarity(vector1, vector2, weights)
                    else:
                        score -= similarity(vector1, vector2)
                    
    # Normalize by the number of comparisons
    n = len(vectors)
    return score / (n*(n-1)/2)
    
def nearestneighbors(text, corpus, mapper, neighbors = 3, similarity=cosinesimilarity):
    """Find the nearest neighbors of a given text in this corpus
    
    Inputs:
        text: text to find neighbors, either as a string or a Text object
        corpus: candidates to neighbors
        mapper: SemanticMapper mapping texts to vector space
        neighbors: number of neighbors to produce
        similarity: function to measure similarity between vectors
    Outputs:
        list: of tuples (similarity, neighbor text)
    """
    # First perform a fast filter by using Elastichsearch usual search routines
    firstsearch = corpus.search(text)    
    # Now compute semantic similarity for all these candidates    
    target = mapper.map(text)
    # First pass to compute most similar
    similarities = [similarity(target, mapper.map(corpustext)) for corpustext in firstsearch]
    indexes = np.argpartition(similarities, -neighbors)[-neighbors:]
    # Second pass to recover them
    mostsimilar = {idx : corpustext for idx, corpustext in enumerate(firstsearch) if idx in indexes}
    # Broadcast similarity factors and text together
    # The text is also returned to a standard string-like form
    outputs = [(" ".join(mostsimilar[idx]), similarities[idx]) for idx in indexes]
    # Sort by similarity
    sortedout = sorted(outputs, key=lambda x: -x[1])
    return sortedout
    
def finetuneweightstags(vectors, tags, wsimilarity=weightedcosinesimilarity, iters = 100):
    """Fine tunes the similarity weights to improve intertag score"""

    dims = vectors.shape[1]

    bestw = None
    bestscore = float("-inf")
    for iter in range(0,iters):
        w = [np.random.normal() for i in range(0,dims)]
        # Evaluate score with this
        score = intertagscore(vectors, tags, w)
        if score > bestscore:
            bestscore = score
            bestw = w
    
    return bestw