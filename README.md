IUPUI Research

LUKE'S FILES:

In my files, the Java files are used for crawling, and the Python files are used 
for phrase extraction, graphing, and most other necessary operations.

Crawling Instructions:

In the crawler, you will need to find the DOIs of papers as inputs. In general, you
need to find the DOI of one paper from a conference/journal to crawl every paper in 
that conference/journal in that year.In order to find the DOIs for an entire conference, 
you need to search the conference in ACM's Proceedings or IEEE's Browse Conferences. 
This should bring up a list of relevant conferences; find the correct conference label.
Next, you should see a list of years for the conference; click on one of those links, 
which should take you to the conference page. Next, follow the steps for ACM/IEEE.

ACM: https://dl.acm.org/

The conference page should be a separate page, so you simply need to click on its 
table of contents. There should be a tab to the Table of Contents on the page; if that 
link doesn't work, change it first to single-page view. Then you should be able to see
a list of papers. Follow one of their links by its DOI or its title. Then you need to 
find the DOI on the page.

The ACM DOI is almost always found in the format "doi>10.1145/DOIPart1.DOIPart2". 
Note that you only include the part after the slash, since the preceding part is always
the same for ACM papers. Be sure to extract both parts of the DOI to be consistent with 
my code's link extraction.

For example, we could have this on an ACM page: "doi>10.1145/1831407.1831423."
Then you should extract "1831407.1831423" for the ACM DOI.

Occasionally, the ACM DOIs are not in this format. For instance, they might include 
the name of the conference in the DOI. This doesn't come up very often, but it would be
good to figure out how to deal with those ones. My ANCS results may be slightly reduced 
by this odd formatting; I should check that.

IEEE: https://ieeexplore.ieee.org/

The conference page should be a list of papers and other conference links. Scroll 
down until you find a link to an actual paper; if this isn't possible, follow a link 
to some useless conference link. Make sure that you do not leave the first page of 
results when looking for links; otherwise, my code may miss some links.

The IEEE DOI is usually found in the format: "DOI:10.1109/conferenceName.year.doi",
but this formatting is less consistent than that in the ACM DL. The best way to follow 
links for IEEE is to use the URL, as it never fails to follow the correct link. In the 
URL, we have the format "https://ieeexplore.ieee.org/document/number/" This "number" is
often the DOI, but even when it isn't, you can use it to follow this link.

For instance, we could have these on an IEEE page: "DOI:10.1109/ASE.1999.802301" 
and "https://ieeexplore.ieee.org/document/802301/" Then you should extract "802301" 
from either the URL or the DOI statement.

**Note that it may be possible to find some way to crawl ACM consistently (like I 
do with IEEE).If you are having trouble with finding the correct DOI format, 
investigate other ways of extracting links.

Once you find the DOI for a paper, you simply add it to a list in the Tester class 
and then move on to the next year in that conference. The Tester class provides 2 
examples of this, including an unfinished run of KDD. Be sure to extract a DOI from a 
paper from each available year of the conference, or else you will miss some data.

That's all for crawling. IEEE conferences take significantly shorter to run than 
ACM conferences.In general, it takes about an hour on average for any reasonably big 
conference for IEEE, but it takes about 2 hours or more for ACM conferences. The 
connection for ACM is just bad too; I often have gotten HTTP error 524 from ACM, which 
is an uncontrollable server error (at least on our end). If ACM acts like it has for 
me, you may need to modify the code to crawl the DL.

The crawling produces a text file, which contains information from each paper. I have
included all of my results as examples. Note that the case in the abstract may be 
different in the examples; don't worry about that.

Phrase Extraction Instructions:

For the phrase extraction, most of the code is nicely laid out in the Python files.
fileIOGrapher.py is used for reading in the input and graphing the final dictionaries,
and classifierChunker.py is used for extracting phrases from the abstracts.
	
The code should be commented well enough that you should be able to follow it 
without more instruction. See the sample usage for examples of how to use the files.	

bigram.py:
The code extracts keyphrases with two words and three words, compute the support for each phrase, 
then use bigram method or relational words method to find is-a relationship between phrases. 
To run the program, simply change the strpath to the new location of the text file. 

word2vec: 
The code extracts abstracts from metadata, extracts bigram keyphrases. It then builds a word2vec model, 
train the model based on user-defined parameters, and graph the clustered word vectors with annotations. 
To run the program, change the strpath to the new location of the text file. To achieve the best graph, 
some experiement with the model parameters is needed. 

