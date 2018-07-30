import pickle                                         #import classifier-saving stuff
from collections import Iterable                      #import Iterable interface
from nltk import ChunkParserI, ClassifierBasedTagger  #import taggers
from nltk.stem.snowball import SnowballStemmer        #import stemmer
from nltk.chunk import conlltags2tree, tree2conlltags #import conversions between chunking forms
from nltk.corpus import conll2000					  #import the training  corpus
import random                                         #import random for shuffling the training data
import fileIOGrapher as fiog					      #import my other file
import nltk                                           

#Returns the features from a set of tokens (essentially copied from a tutorial)
#tokens is the tagged sentence
#index is the index of the current word
#history describes the previous predictions (I, O, or B)
def features(tokens, index, history):
    
    stemmer = SnowballStemmer('english') #init the stemmer
    tokens = [('__START2__', '__START2__'), ('__START1__', '__START1__')] + list(tokens) + [('__END1__', '__END1__'), ('__END2__', '__END2__')]
    history = ['__START2__', '__START1__'] + list(history) #pad the lists with placeholders
    index += 2 # shift the index by 2 due to the padding
 
    word, pos = tokens[index]                      #unpack current (word, PoS) tuple
    prevword, prevpos = tokens[index - 1]          #unpack previous (word, PoS) tuple
    prevprevword, prevprevpos = tokens[index - 2]  #unpack the (word, PoS) tuple two back
    nextword, nextpos = tokens[index + 1]		   #unpack next (word, PoS) tuple
    nextnextword, nextnextpos = tokens[index + 2]  #unpack the (word, PoS) tuple two forward
 
    return {
        'word': word,
        'lemma': stemmer.stem(word), #return all of the features
        'pos': pos,
        'next-word': nextword,
        'next-pos': nextpos,
        'next-next-word': nextnextword,
        'nextnextpos': nextnextpos,
        'prev-word': prevword,
        'prev-pos': prevpos,
        'prev-prev-word': prevprevword,
        'prev-prev-pos': prevprevpos,
    }
 
#A class that extends the ChunkParser interface. This defines the framework for the classifier chunker.
#This was essentially copied from a tutorial.
class ClassifierChunkParser(ChunkParserI):

	#Constructor
    def __init__(self, chunked_sents, **kwargs):
        chunked_sents = [tree2conlltags(sent) for sent in chunked_sents] #converts the sentences to IOB form
        chunked_sents = [[((word, pos), chunk) for (word, pos, chunk) in sent] for sent in chunked_sents] #convert from triplets to pairs
        #self.feature_detector = features
        self.tagger = ClassifierBasedTagger(train=chunked_sents, feature_detector=features, **kwargs) #init the tagger
 
	#Parses the tagged sentences and returns the chunks in the IOB format
    def parse(self, tagged_sent):
        chunks = self.tagger.tag(tagged_sent) #tag the sentences
        iob_triplets = [(w, t, c) for ((w, t), c) in chunks] #convert from pairs to triplets
        return iob_triplets #convert to tree format
 
#Preprocesses the document into sentences and words and tags each word with its PoS
def preprocess(document):
	sentenceList = nltk.sent_tokenize(document) #split the document into sentences
	sentWords = [nltk.word_tokenize(sent) for sent in sentenceList] #split the sentences into words
	sentWordPoS = [nltk.pos_tag(sent) for sent in sentWords] #tag each word with its PoS
	return sentWordPoS

#Initializes the classifier chunker, saving it to a file. You can read the file after the first run to
#save a little bit of training time.
def initChunker():
	#trainingSents = list(conll2000.chunked_sents()) #get the ConLL-2000 corpus 
	#random.shuffle(trainingSents) #shuffle the corpus 
	#classifier = ClassifierChunkParser(trainingSents) #init the chunker
	#save_classifier = open("chunker.pickle","wb") #open a new classifier file
	#pickle.dump(classifier, save_classifier) #saves the classifier
	#save_classifier.close()
	classifier_f = open("chunker.pickle", "rb") #load the classifier file
	classifier = pickle.load(classifier_f) #read the classifier
	classifier_f.close()
	return classifier

#Removes the given stop words from the chunked sentences and adjusts the "B-NP" tag if necessary.
#NOTE-This method may need tweaking if the results seem fishy. Or it could be done after getting all of the chunks.
def removeStopWords(chunkedSent, stopWords):
	cleanedSent = [] #init a new set of chunked sentences
	checkNext = False #init the flag (be careful with this)
	for i in range(len(chunkedSent)):
		triple = chunkedSent[i]
		if triple[0] in stopWords:  #ignore the stop words
			if triple[2] == 'B-NP': #update the chunk start flag if that part was removed
				checkNext = True
		elif checkNext and triple[2] == 'I-NP': #add a B label if the chunk start flag is on
			cleanedSent.append((triple[0], triple[1], 'B-NP'))
			checkNext = False #reset the flag 
		else: #otherwise add the same triple and reset the flag
			cleanedSent.append(triple)
			checkNext = False
	return cleanedSent

#Returns a list of phrases from the abstract. This relies on the 
def findPhrases(paperAbs):
	phraseList = []
	stopWords = set(nltk.corpus.stopwords.words("english")) #the standard list of stop words
	stopWords |= set(["(",")","[","]",".",",","!","{","}", "``", "''"]) #add punctuation to the stop list
	for sent in paperAbs:
		chunkedSent = classifierChunker.parse(sent) #chunks the sentences in IOB format
		chunkedSent = removeStopWords(chunkedSent, stopWords) #removes the stop words/punctuation
		length = len(chunkedSent)
		for i in range(length):
			triple = chunkedSent[i]
			if(triple[2] == 'B-NP'): #look for the beginning of the chunks
				phrase = triple[0] #add the first one
				while i < length-1 and chunkedSent[i+1][2] == 'I-NP': #continue until the end of the chunk
					phrase += ' ' + chunkedSent[i+1][0] #append the words together
					i += 1
				if len(phrase.split()) > 1: #ignore one-word phrases
					phraseList.append(phrase)
	return phraseList

#This is the main code here
conList = ["ANCS", "MobiCom", "OOPSLA"]
classifierChunker = initChunker() #initialize the chunker
conName = "NAME"
paperList = fiog.readFile("ACM-" + conName + ".txt") #read the file and generate the paper list
for i in range(len(paperList)):
	paper = paperList[i]
	paperAbs = preprocess(paper.abstract) #preprocess the abstract
	phrases = findPhrases(paperAbs) #find the keyphrases in the abstract
	paper.keyphrases += phrases #append these to the keyword list
dict, globalDict = fiog.genDicts(paperList) #generate the dictionaries from the updated set of keywords
try:
	file = open("..\\PhraseFiles\\ACM-" + conName + "-Phrases.txt", "w", encoding="utf-8")
	keyList = sorted(globalDict.keys(), key = globalDict.get, reverse = True) #sort the key list in reverse order
	file.write(str(len(keyList)) + "\n")
	for key in keyList:
		file.write(key + ": " + str(dict[key]) + "\n")
	print("Finished " + conName + "!")
finally:
	file.close()
#add other code here