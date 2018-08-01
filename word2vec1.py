##cluster phrases
from nltk.corpus import PlaintextCorpusReader
import re
import sys
import nltk
from nltk import bigrams
import operator
import pandas as pd
import gensim
# imports needed and logging
import gzip
import gensim 
import logging
import string
from string import punctuation
import nltk.collocations
import nltk.corpus
import collections
from nltk.collocations import *
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stopwords = stopwords.words('english') ##load english stopwords list
   
def findabstract(string, c= 0): ##use recursion to extract abstracts from the data crawled
        startpos = string.find("None")
        #print("left index is" + str(startpos+4))
        if startpos > -1:
            #string = string[left_bracket+1:]
            endpos = string.find("[")
            #print("right index is" + str(endpos-1))
            if endpos > -1:
                abstract.append(string[startpos+9:endpos-1])
                #string.split('[', 1)[0].split(']')[1]
                #print("this keyword is" + abstract[c])
                if string[:endpos].find("[") == -1:
                    c += 1
                string = string[endpos + 1:]
            return findabstract(string)
        else:
            return abstract
        
        
sys.setrecursionlimit(2000) ##set the allowed recursion level higher than default
strPath = "C:\\Users\\simin\\Desktop\\IEEE-ASE.txt" ##load the data
f = open(strPath)
strText = f.read() ##read file
abstract = []
abstract = findabstract(strText) ##make a list of strings of abstracts



import string
for i in range(len(abstract)):
  exclude = set(string.punctuation)
  abstract[i] = ''.join(ch for ch in abstract[i] if ch not in exclude) ##get rid of punctuations in every abstract
  abstract[i] = ''.join(ch for ch in abstract[i] if not ch.isdigit()) ##get rid of digits in every abstract

    
stoplist = set('for a of the and to in both most other then each through while some where them if even many'.split()) ##additional user-defined stopwords 
texts=[[word for word in abstract.lower().split() if word not in stoplist]for abstract in abstract] ##iterate through to get rid of user-defined stopwords

# remove words that appear only once
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
     for token in text:
         frequency[token] += 1
texts2 = [[token for token in text if frequency[token] > 1]## filter out words that only occured once
          for text in texts] ##tokenize the abstracts
dictionary = gensim.corpora.Dictionary(texts2) ##load gensim dictionary mapping words to IDs
dictionary.save('C:\\Users\\simin\\desktop\\bigram.txt') ##save dictionary
# store the dictionary, for future reference
new_doc = "abstract bigram" 
new_vec = dictionary.doc2bow(new_doc.lower().split()) ## make everything into lower case
corpus = [dictionary.doc2bow(text) for text in texts] ## change into bag-of-words format
print("done corpus")

import string
from string import punctuation
import nltk.collocations
import nltk.corpus
import collections
from nltk.collocations import *
from nltk.tokenize import word_tokenize

###bigrams
grammar = [[]]*len(texts2) ##make empty list of lists
for i in range(len(texts2)):
  tmpstr = ' '.join(texts2[i]) ##join words to make longer strings
  translator = str.maketrans('', '', string.punctuation) ##remove punctuation, join to space
  tmpstr = tmpstr.translate(translator)
  #print(tmpstr)
  bgm = nltk.collocations.BigramAssocMeasures() #use nltk bigram collocation
  tgm = nltk.collocations.TrigramAssocMeasures() #use nltk trigram collocation
  finder = nltk.collocations.BigramCollocationFinder.from_words(word_tokenize(tmpstr))
  finder.apply_freq_filter(2) ## at least occured twice
  scored = finder.score_ngrams(bgm.likelihood_ratio) ## how likely are the two words occur together 
  features = finder.nbest(bgm.likelihood_ratio, 100) ##use the top hundred most likely bigrams
  #print(features)
  for j in range(len(features)):
      tmp =nltk.pos_tag(features[j])
      if (tmp[0][1] == 'NN' and tmp[1][1] == 'NN') or (tmp[0][1] == 'JJ' and tmp[1][1] == 'NN'):
          tmpstr = ' '.join(list(features[j]))
          grammar[i].append(tmpstr)
print("done grammar")


from matplotlib import *
import plotly
import matplotlib.pyplot as plt
import numpy as np
import plotly.plotly as py
import plotly.graph_objs as go
from sklearn.manifold import TSNE
model = gensim.models.Word2Vec(grammar, size = 300, window = 50, min_count = 3000, workers = 5000)
## use gensim word2vec method, start a new model
##grammar is the phrase corpus
##vector size for each phrase (dimension)
##window of context
##min_count: minimum count of occurence threshold for phrases
##wokers: number of worker threads 
model.train(grammar, total_examples = len(grammar), epochs = 500)
## train the model with 500 iterations
print("done model")
def tsne_plot(model):
## t-distributed stochastic neighboring entities
## used for dimensionality reduction, for visualization of high-dimensional datasets
    "Creates and TSNE model and plots it"
    labels = []
    tokens = []

    for word in model.wv.vocab:
        tokens.append(model[word])
        labels.append(word)
    
    tsne_model = TSNE(perplexity=40, n_components=2, init='pca', n_iter=3000, random_state=23)
    new_values = tsne_model.fit_transform(tokens)

    x = []
    y = []
    for value in new_values:
        x.append(value[0])
        y.append(value[1])
        
    plt.figure(figsize=(16, 16)) 
    for i in range(len(x)):
        plt.scatter(x[i],y[i])
        plt.annotate(labels[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')
    plt.show()
##graphing
##T-SNE
tsne_plot(model)
