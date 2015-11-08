# -*- coding: utf-8 -*-
"""
Module for computing semantic embedding of texts.

@author: Álvaro Barbero Jiménez
"""

import numpy as np
from gensim.models import Word2Vec
from polyglot.mapping import Embedding, DigitExpander, CaseExpander
from scipy.interpolate import interp1d

from text import Text

def loadembedding(filename):
    """Loads a precomputed embedding into memory
    
    Input:
        filename: of the model file
    Output:
        embedding object
    """
    embedding = Embedding.load(filename)
    # Apply useful extensions
    embedding.apply_expansion(DigitExpander)
    # We might need this if we want to ignore case
    # embedding.apply_expansion(CaseExpander)
    return embedding

def embeddingbyall(text, embeddings):
    """Computes an extended embedding for a text by using many approaches.
    
    Inputs:
        text: text to embed in a vector space
        embeddings: iterable of embeddings to apply
        
    Output:
        Vector representation of the text.
    """
    
    vector = []
    for embedding in embeddings:
        vector.extend(embeddingbywordmean(text, embedding))
        
    return np.array(vector)

def embeddingbywordmean(text, embedding):
    """Computes the semanting embedding of a text as the mean of word meanings
    
    Inputs:
        text: text to embed. Must be provided as a list of tokens.
        embedding: embedding of words to use.
        
    Output:
        Vector representation of the text.
    """

    # Sum all the known word embeddings
    vector = np.zeros(embedding.shape[1])
    for word in text:
        if word in embedding:
            vector += np.array(embedding[word])
            
    # Normalize by number of words
    vector /= len(text)
    return vector
    
def embeddingbyinterpolation(text, embedding, n=100):
    """Computes the semanting embedding of a text as the interpolation of word meanings
    
    Inputs:
        text: text to embed. Must be provided as a list of tokens.
        embedding: embedding of words to use.
        n: number of points in the interpolation
        
    Output:
        Vector representation of the text.
    """
    
    # Compute all word embeddings into a matrix
    matrix = np.vstack([np.array(embedding[word]) for word in text if word in embedding])
    # Interpolate
    nd = matrix.shape[1]
    x = np.linspace(0,nd,nd)
    xi = np.linspace(0,nd,n)
    intf = interp1d(x, matrix, axis=1)
    yi = intf(xi)
    return yi.vectorize()
 
def computewordembedding(texts):
    """Creates a new word embedding using a given list of tokenized texts"""
    # Compute model
    model = Word2Vec(texts, size=100, window=5, min_count=5, workers=8)
    # Transform to polyglot model
    return Embedding.from_gensim(model)
   
def crossdistances(vectors):
    """Computes the matrix of cross distances among all pairs of vectors
    
    Inputs:
        vectors: list of vectors for which to compute distances
        
    Output:
        Numpy matrix of distances
    """
    return np.array([[np.linalg.norm(a-b) for a in vectors] for b in vectors])
    
def crosssimilarities(vectors):
    """Computes the matrix of cross similarities among all pairs of vectors
    
    Inputs:
        vectors: list of vectors for which to compute distances
        
    Output:
        Numpy matrix of distances
    """
    return 1-crossdistances(vectors)
    
class SemanticMapper():
    """Class for transforming texts to a semantic vector space"""
    
    def __init__(self, embeddings, mappingfunction):
        """Create a new semantic mapper

        Inputs:
            embeddings: list of Embedding objects to use
            mappingfunction: function that receives a text and a set of
                embeddings, and returns a vector representation
        """
        self._embeddings = embeddings
        self._mappingfunction = mappingfunction
        
    def map(self, text):
        """Transforms the given text to a semantic vector
        
        Inputs:
            text: string or Text object to map
            
        Outputs:
            vectorized semantic representation of the text
        """
        if isinstance(text, Text):
            textok = text
        else:
            textok = Text(text)
        return self._mappingfunction(textok, self._embeddings)
