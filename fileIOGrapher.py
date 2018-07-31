import matplotlib.pyplot as mpp #graphing library

#container for the research data - mostly acts as a 3-tuple but is mutable
class ResearchPaper:
	date = 0  #the publication date
	abstract = "" #the abstract text
	keyphrases = "" #the user-generated keyphrases
	
	#constructor that initializes the variables
	def __init__(self, y, a, k):
		self.date = y     #read the year
		self.abstract = a.lower() #read the abstract in lowercase (should be unnecessary)                         
		self.keyphrases = k[1:len(k)-1].split(", ") #split the list and ignore the braces
		self.keyphrases = [keyphrase.lower() for keyphrase in self.keyphrases if len(keyphrase.split()) > 1] #discard one-word keyphrases and take them in lowercase
	
	#debugging
	def printSelf(self):
		print(self.conference + "\n" + str(self.date) + "\n" + self.abstract + "\n" + str(self.keywords))

#reads the file and returns a list of papers
def readFile(fileName):
	try: #WATCH THE PATH
		f = open("path" + fileName, encoding="utf-8")
		length = int(f.readline().strip())   #read the number of papers
		paperList = [] 
		while length > 0:
			f.readline()                     #discard the title
			f.readline()                     #discard the conference name
			f.readline()                     #discard the journal name
			year = int(f.readline().strip()) #read the publication date
			ab = f.readline().strip()        #read the abstract text
			k = f.readline().strip()         #read the keyword list
			paperList.append(ResearchPaper(year, ab, k))
			length -= 1
		return paperList
	finally: 
		f.close()                            #close the file at the end

#generates dictionaries from the list of keyphrases in paper list
def genDicts(paperList):
	globalDict = {}  #init global dictionary for the total count of phrases
	dict = {}        #init local dictionary that tracks the yearly frequency of the phrases
	for paper in paperList:
		for keyphrase in paper.keyphrases:
			year = paper.date
			if keyphrase in dict:
				if year in dict[keyphrase]: 
					dict[keyphrase][year] += 1 #add to the yearly frequency
				else:
					dict[keyphrase][year] = 1  #init the yearly frequency for that year
			else:
				dict[keyphrase] = {year: 1}    #init the yearly frequency for that keyphrase
			if keyphrase in globalDict: 
				globalDict[keyphrase] += 1     #add to the global frequency
			else:
				globalDict[keyphrase] = 1      #init the global frequency for that keyphrase
	return cleanDicts(dict, globalDict)        #return the cleaned dictionaries

#removes rare phrases from the dictionaries
def cleanDicts(dict, globalDict):
	toBeDeleted = []
	for key in globalDict.keys():
		if globalDict[key] <= 2:
			toBeDeleted.append(key) 
	for phrase in toBeDeleted:
		globalDict.pop(phrase)  #delete keys from the dictionaries with 2 or less frequency
		dict.pop(phrase)
	return (dict, globalDict)

#displays the frequency of each keyphrase in keyphraseList on a line graph
def dispKeyphrases(dict, keyphraseList, conName):
	colorList = ['red', 'green', 'blue', 'black'] #limited to four keyphrases currently
	i = 0
	for keyphrase in keyphraseList:
		yearDict = dict[keyphrase]
		sortedYearList = sorted(list(yearDict.keys())) #sort the year list to produce nice trends
		mpp.plot(sortedYearList, [yearDict[year] for year in sortedYearList], color = colorList[i], label = keyphrase.title(), lineWidth=1)
		i += 1 #plot the line for each keyphrase
	mpp.title(conName)
	mpp.xlabel("Year") #label the axes
	mpp.ylabel("Frequency")
	mpp.legend(loc = "best") #add the legend
	mpp.show() #be careful with the axis ticks - they can be weird

#SAMPLE USAGE
#paperList = readFile("IEEE-ASE.txt") #read the file and generate the paper list
#dict, globalDict = genDicts(paperList)
#keyList = sorted(globalDict.keys(), key = globalDict.get, reverse = True) #sort the key list in reverse order
#for i in range(20):
#	dispKeyphrases(dict, [keyList[i],keyList[i+1]], "ASE")
