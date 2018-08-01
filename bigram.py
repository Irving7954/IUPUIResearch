
from nltk.corpus import PlaintextCorpusReader
import re
import sys
from rake_nltk import Rake
import RAKE.RAKE as rake
import nltk
from nltk import bigrams, trigrams
import operator
import pandas as pd
import gensim
import nltk.collocations
import nltk.corpus
import collections

def findyear(string, c= 0):
        startpos = string.find("None")
        if startpos > -1:
            #string = string[left_bracket+1:]
            endpos = string.find("[")
            if endpos > -1:
                years.append(string[startpos+4:startpos+9])
                #string.split('[', 1)[0].split(']')[1]
                if string[:endpos].find("[") == -1:
                    c += 1
                string = string[endpos + 1:]
            return findyear(string)
        else:
            return years
        
def findabstract(string, c= 0):
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

sys.setrecursionlimit(5000)
strPath = "C:\\Users\\simin\\Desktop\\IEEE-ASE.txt"
f = open(strPath)
strText = f.read()
abstract = []
abstract = findabstract(strText)
print("done abstract")
years = []
years = findyear(strText)

stoplist = set('for a of the and to in both most other then each through while some where them if even many'.split())
texts=[[word for word in abstract.lower().split() if word not in stoplist]for abstract in abstract]

# remove words that appear only once
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
     for token in text:
         frequency[token] += 1
texts2 = [[token for token in text if frequency[token] > 1]
          for text in texts]
dictionary = gensim.corpora.Dictionary(texts2)
dictionary.save('C:\\Users\\simin\\desktop\\trigram.txt')
# store the dictionary, for future reference
new_doc = "abstract triigram"
new_vec = dictionary.doc2bow(new_doc.lower().split())
corpus = [dictionary.doc2bow(text) for text in texts]


import string
from string import punctuation
import nltk.collocations
import nltk.corpus
import collections
from nltk.collocations import *
from nltk.tokenize import word_tokenize


####generate trigrams
wholedoc = []
for i in range(len(texts2)):
    wholedoc += texts2[i]
    
tmpstr = ' '.join(wholedoc)
translator = str.maketrans('', '', string.punctuation)
tmpstr = tmpstr.translate(translator)
#print(tmpstr)
#bgm = nltk.collocations.BigramAssocMeasures()
tgm = nltk.collocations.TrigramAssocMeasures()
finder = nltk.collocations.TrigramCollocationFinder.from_words(word_tokenize(tmpstr))
finder.apply_freq_filter(2) ## at least occured twice
scored = finder.score_ngrams(tgm.likelihood_ratio)
features= finder.nbest(tgm.likelihood_ratio, 10000)
grammar = []
for i in range(len(features)):
    tmp =nltk.pos_tag(features[i])
    if (tmp[0][1] == 'NN' and tmp[1][1] == 'NN' and tmp[2][1] == 'NN') or (tmp[0][1] == 'JJ' and tmp[1][1] == 'NN' and tmp[2][1] == 'NN') or (tmp[0][1] == 'NN' and tmp[1][1] == 'NN' and tmp[2][1] == 'NN'):
        ## tag the position of words syntactically
        ## only choose noun phrases
        tmpstr = ' '.join(list(features[i]))
        tmpstr = tmpstr.translate(translator)
        #print(tmpstr)
        finder = nltk.collocations.TrigramCollocationFinder.from_words(word_tokenize(tmpstr))
        scored = finder.score_ngrams(tgm.likelihood_ratio)
        grammar += scored
#print(grammar)

tri_dict = {}
for i in range(len(grammar)):
    for j in range(len(abstract)):
        phrase = ' '.join(grammar[i][0]) ## join words together into phrases
        count = abstract[j].count(phrase) ## count number of occurences in the abstract
        if count != 0:
            year = years[j]
            if phrase in tri_dict.keys(): #key already exist
                    #print(global_dict[phrase])
                    tmplist =[]
                    for k in range(len(tri_dict[phrase])): 
                        tmplist.append(tri_dict[phrase][k][0]) ## append the local frequency with the phrase into dictionary
                    if year in tmplist: #exist key, exist year
                        for k in range(len(tri_dict[phrase])):
                            tri_dict[phrase][k][1] += count ## aggregate the count of the phrase
                            break 
                    else:
                        tri_dict[phrase].append([year, count]) #exist key, new year
                        ## add a new key into the dictionary with the year and count
            else: #new key
                tri_dict[phrase] = [[year, count]]
print('done tri_dict')
#print(len(tri_dict.keys()))

trisupport_dict = {}
for i in range(len(tri_dict.keys())):
    for j in range(len(abstract)):
        phrase = list(tri_dict.keys())[i]
        count = abstract[j].count(phrase)
        if count != 0:
            if phrase in tri_dict.keys(): #key already exist
                    #print(global_dict[phrase])
                if phrase in trisupport_dict.keys():
                    trisupport_dict[phrase] += 1
                else: #new key
                    trisupport_dict[phrase] = 1
#print(trisupport_dict)'''



###generate bigrams
wholedoc = []
for i in range(len(texts2)):
    wholedoc += texts2[i]
    
tmpstr = ' '.join(wholedoc)
translator = str.maketrans('', '', string.punctuation) ## get rid of punctuations 
tmpstr = tmpstr.translate(translator) 
bgm = nltk.collocations.BigramAssocMeasures()
finder = nltk.collocations.BigramCollocationFinder.from_words(word_tokenize(tmpstr)) ##tokenize words into two word phrases
finder.apply_freq_filter(2) ## at least occured twice
scored = finder.score_ngrams(bgm.likelihood_ratio)
features= finder.nbest(bgm.likelihood_ratio, 10000) ## pick the top ten thousand phrases that are most likely to occur
grammar = []
for i in range(len(features)):
    tmp =nltk.pos_tag(features[i])
    if (tmp[0][1] == 'NN' and tmp[1][1] == 'NN' ) or (tmp[0][1] == 'JJ' and tmp[1][1] == 'NN' ):
        try: 
            tmpstr = ' '.join(list(features[i]))
            tmpstr = tmpstr.translate(translator)
            finder = nltk.collocations.BigramCollocationFinder.from_words(word_tokenize(tmpstr))
            scored = finder.score_ngrams(bgm.likelihood_ratio)
            grammar += scored
            print(tmpstr)
        except ValueError:
            break
#print(grammar)

bi_dict = {}
for i in range(len(grammar)):
    for j in range(len(abstract)):
        phrase = ' '.join(grammar[i][0])
        count = abstract[j].count(phrase)
        if count != 0:
            year = years[j]
            if phrase in bi_dict.keys(): #key already exist
                    #print(global_dict[phrase])
                    tmplist =[]
                    for k in range(len(bi_dict[phrase])):
                        tmplist.append(bi_dict[phrase][k][0])
                    if year in tmplist: #exist key, exist year
                        for k in range(len(bi_dict[phrase])):
                            bi_dict[phrase][k][1] += count
                            break
                    else:
                        bi_dict[phrase].append([year, count]) #exist key, new year
            else: #new key
                bi_dict[phrase] = [[year, count]]
print('done bi_dict')
#print(len(bi_dict.keys()))

bisupport_dict = {}
for i in range(len(bi_dict.keys())):
    for j in range(len(abstract)):
        phrase = list(bi_dict.keys())[i]
        count = abstract[j].count(phrase) ## calculate support by count the number of time the phrase occurred in the conference
        if count != 0:
            if phrase in bi_dict.keys(): #key already exist
                    #print(global_dict[phrase])
                if phrase in bisupport_dict.keys():
                    bisupport_dict[phrase] += 1
                else: #new key
                    bisupport_dict[phrase] = 1
print(bisupport_dict)
                
## is a using structure
isA = []
for bikey in bi_dict.keys():
    for trikey in tri_dict.keys():
        trispace = trikey.index(" ")
        ## if last two words of trigrams have the same two words as bigrams, is-a relationship detected
        if (bikey == trikey[trispace+1:]) and (bisupport_dict[bikey] > trisupport_dict[trikey] >= 2):
            print("match")
            isA.append([trikey, bikey])
print(isA)


support_dict = {}
support_dict = {**bisupport_dict, **trisupport_dict}
## is a using conjunction
isA1 = {}
## list of conjunction words, used to detect relationships
conjunction = ['such as', 'for example', 'including', 'for instance', 'e.g.', 'like', 'in particular', 'sort of']
## index offset list 
length = [7, 11, 9, 12, 4, 4, 13, 7]
keyphrase = list(bi_dict.keys()) + list(tri_dict.keys())
print(keyphrase)
for i in range(len(abstract)):
    for j in range(len(conjunction)):
        for k in range(len(keyphrase)):
            if conjunction[j] in abstract[i]:
                conjunction_ind = abstract[i].index(conjunction[j]) ##find the index of  the conjunction words
                offset = length[j]
                try:
                    if keyphrase[k] in abstract[i][conjunction_ind-30:conjunction_ind]: ## search previous 30 characters for the keyphrases
                       isA1[keyphrase[k]] = []
                       for m in range(len(keyphrase)):
                            if keyphrase[m] in abstract[i][conjunction_ind+offset:conjunction_ind+offset+30] and (support_dict[keyphrase[k]] > support_dict[keyphrase[m]] >=2) : ## search the next 30 characters for keyphrases plus offset
                                #print('found leaf') 
                                isA1[keyphrase[k]].append(keyphrase[m])
                except ValueError:
                    break

for key in [ k for (k,v) in isA1.items() if not v ]:
  del isA1[key]
print("done relations")
print(isA1)

