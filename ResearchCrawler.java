/**
* Crawls the ACM DL and IEEE Xplore DL by conference/journal, extracting metadata as it goes.
* See the code for more details.
* @author Luke Schoeberle
* @author Sam Guenette, David Bis (Crawler Part)
*/

import java.io.BufferedInputStream;
import java.io.File;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Scanner;

public class ResearchCrawler {
	static final String ACM_START_URL = "https://dl.acm.org/citation.cfm?doid="; //uses doi ID
	
	static final String ACM_END_URL = "&preflayout=flat"; //turns on single-page view instead of tabbed view
	
	static final String IEEE_BASE_URL = "https://ieeexplore.ieee.org"; //uses last number (doi) - needs /document or /xpl first
	
	private byte numRequests; //the number of requests since the last delay
	
	private int extraLinksVisited; //the number of extraneous conference links visited so far
	
	private static PrintWriter outputPW; //PrintWriter to create the output file
	
	//initializes the crawler
	public ResearchCrawler(String fileName) throws Exception {
		numRequests = 0; //init stuff
		extraLinksVisited = 0;
		outputPW = new PrintWriter(new File(fileName)); //WATCH THE PATH
	}
	
	//gets the text from the URL specified
	private String getURLText(String url) throws Exception { 
		HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection(); //open a connection
		connection.addRequestProperty("User-Agent", "Mozilla/4.76"); //add a user agent to not look like a bot
		if(++numRequests % 5 == 0) {
			Thread.sleep(3000); //sleep after every 5 requests 
			numRequests = 0; //reset the count to avoid overflow issues
		}
		Scanner scanner = new Scanner(new BufferedInputStream(connection.getInputStream()));
		scanner.useDelimiter("\\Z"); //read the whole file
		String content = scanner.next();
		scanner.close();
		return content;
	}
	
	//replaces strange HTML encodings and other strange encodings
	private String getProcessedText(String text) { 
		text = text.replace("<p>", "");
		text = text.replace("</p>", "");
		text = text.replace("<par>", "");
		text = text.replace("</par>", ""); //replace tags
		text = text.replace("<i>", "");
		text = text.replace("</i>", "");
		text = text.replace("<b>", "");
		text = text.replace("</b>", "");
		text = text.replace("<inf>", "");
		text = text.replace("</inf>", "");
		text = text.replace("<sup>", "");
		text = text.replace("</sup>", "");
		text = text.replace("&iuml;","\u00EF"); //replace i umlauts
		text = text.replace("&uuml;","\u00FC"); //replace u umlauts
		text = text.replace("&#x00F6;","\u00F6"); //replace o umlauts
		text = text.replace("&nbsp;", " "); //replace special spaces
		text = text.replace("&rdquo;", "\""); //replace stupid left quotes
		text = text.replace("&ldquo;", "\""); //replace stupid right quotes
		text = text.replace("&#38;", "&"); //replace strange encoding 1
		text = text.replace("\\\"", "\""); //replace escape sequences
		text = text.replace("&#x0022;", "\""); //replace strange encoding 2
		text = text.replace("&lambda;", "\u03bb"); //replace lambda
		text = text.replace("&delta;", "\u03b4"); //replace delta
		text = text.replace("&Pi;", "\u03A0"); //replace big pi
		text = text.replace("&omega;", "\u03C9"); //replace little omega
		text = text.replace("&#x00AE;", "\u00AE"); //replace restricted sign
		text = text.replace("&#x03BC;", "\u03BC"); //replace little micro
		text = text.replace("\n", ""); //remove new lines
		text = text.replace("&mdash;", "-"); //replace m-dash
		text = text.trim(); //trim extra spaces
		return text;
	}
	
	//crawls the ACM DL, starting at each of the seeds. Note that each seed should be from a different conference/journal
	public void crawlACM(ArrayList<String> seeds) throws Exception {
		String graphData = ""; //String for reducing File I/O cost
		HashSet<String> visited = new HashSet<>(); //visited set
		Queue<String> q = new LinkedList<>(); //queue for BFS
		String currentText = null; //placeholder for the current text
		q.addAll(seeds);
		visited.addAll(seeds); //add the seeds to both places
		while(!q.isEmpty()) {
			String doi = q.poll(); //pop the stop
			currentText = getACMText(doi); //get the text
			graphData += "\n" + getACMTitle(currentText) + "\n";
			graphData += getACMConference(currentText) + "\n";
			graphData += getACMJournal(currentText) + "\n"; //get all the necessary text
			graphData += getACMDate(currentText) + "\n";
			graphData += getACMAbstract(currentText) + "\n";
			graphData += getACMKeywords(currentText).toString();
			addACMLinks(currentText, visited, q); //add the conferences links if they have not been already added
		}
		outputPW.println(visited.size() + graphData); //print the results to the file
		outputPW.close();
	}
	
	//gets the ACM HTML text from the specified DOI
	public String getACMText(String doi) throws Exception { 
		String text = getURLText(ACM_START_URL + doi + ACM_END_URL); //get the HTML text
		return text;
	}
	
	//returns the title from an ACM page. This should only be called on an ACM HTML text
	private String getACMTitle(String text) { 
		int tiStartIndex = text.indexOf("citation_title")+ 25; //find the title field (and skip to the starting quote)
		int tiEndIndex = text.indexOf('\"', tiStartIndex); //find the terminating quote
		String tiText = text.substring(tiStartIndex, tiEndIndex); //get the title
		tiText = getProcessedText(tiText); //replace invalid stuff
		return tiText;
	}
	
	//returns the conference from an ACM page if applicable. Note that this functionality is not currently relevant in the crawler
	private String getACMConference(String text) { 
		int coStartIndex = text.indexOf("citation_conference"); //find the conference field
		if(coStartIndex < 0)
			return "None"; //return None if it did not come from a conference
		coStartIndex += 30; //advance the index to the necessary text
		int coEndIndex = text.indexOf('\"', coStartIndex); //find the terminating quote
		String coText = text.substring(coStartIndex, coEndIndex); //get the conference
		coText = getProcessedText(coText); //replace invalid stuff
		return coText;
	}
	
	//returns the journal from an ACM page if applicable. Note that this functionality is not currently relevant in the crawler
	private String getACMJournal(String text) { 
		int joStartIndex = text.indexOf("citation_journal_title"); //find the title field
		if(joStartIndex < 0)
			return "None"; //return None if it did not come from a journal
		
		joStartIndex += 33; //advance the index beyond the first quote
		int joEndIndex = text.indexOf('\"', joStartIndex); //find the terminating quote
		String joText = text.substring(joStartIndex, joEndIndex); //get the journal title
		
		joStartIndex = text.indexOf("citation_volume", joStartIndex) + 26; //advance beyond the first quote
		joEndIndex = text.indexOf('\"', joStartIndex); //find the terminating quote
		joText += " VOLUME " + text.substring(joStartIndex, joEndIndex); //get the volume and add it on
		
		joStartIndex = text.indexOf("citation_issue") + 25; //advance beyond the first quote
		joEndIndex = text.indexOf('\"', joStartIndex); //find the terminating quote
		joText += " ISSUE " + text.substring(joStartIndex, joEndIndex); //get the issue and add it on
		
		joText = getProcessedText(joText); //replace invalid stuff
		return joText;
	}
	
	//returns the publication year from an ACM page
	private String getACMDate(String text) { 
		int daStartIndex = text.indexOf("citation_date")+ 24; //find the date field 
		int daEndIndex = text.indexOf('\"', daStartIndex); //find the terminating quote
		String daText = text.substring(daStartIndex, daEndIndex); //get the date (it comes in the format xx/XX/xxxx)
		daText = daText.split("/")[2]; //keep only the year
		daText = getProcessedText(daText); //replace invalid stuff
		return daText;
	}
	
	//returns the abstract text from an ACM page if applicable
	private String getACMAbstract(String text) { 
		int abIndex = text.indexOf("NAME=\"abstract\""); //find the abstract field
		int startAbIndex = text.indexOf("display:inline", abIndex); //find the abstract text
		int endAbIndex = text.indexOf("</div>", abIndex); //find concluding div tag
		if(startAbIndex < 0 || startAbIndex > endAbIndex)
			return "None"; //there is no text if no display:inline exists
		startAbIndex += 16;
		String abText = text.substring(startAbIndex, endAbIndex); //get the abstract text
		abText = getProcessedText(abText).toLowerCase(); //replace invalid stuff and make it lowercase
		return abText;
	}
	
	//returns the Index Terms from an ACM page, which we treat as keyphrases in this project
	private HashSet<String> getACMKeywords(String text) { 
		HashSet<String> indexTermList = new HashSet<>(); //use HashSet to eliminate duplicates
		int startIndex = text.indexOf("data.addRows"); //find the index term area
		int lastIndex = text.indexOf("]);", startIndex); //keep track of the end of the block
		int endIndex = 0;
		for(;;) {
			startIndex = text.indexOf('>', startIndex); //get the beginning of the term
			if(startIndex > lastIndex) //end if we left the index term block
				break;
			startIndex++; //increment past this >
			if(text.charAt(startIndex) == '<') //get past the >< pattern if it occurs
				startIndex = text.indexOf('>', startIndex)+ 1; //move past the > again
			endIndex = text.indexOf('<', startIndex); //find the terminating <
			String indexTerm = text.substring(startIndex, endIndex); //get the term
			indexTerm = getProcessedText(indexTerm).toLowerCase(); //replace invalid stuff and make them lowercase
			indexTermList.add(indexTerm);
			startIndex = text.indexOf("]", startIndex); //move on to the next term
		}
		indexTermList.remove("CCS for this Article"); //remove the redundant first element - as it appears in every abstract
		return indexTermList;
	}
	
	//adds the DOIs from the Table of Contents of the journal/conference from an ACM page to the visited set and the queue
	private void addACMLinks(String text, HashSet<String> visited, Queue<String> q) { 
		int startIndex = 0, endIndex = 0;
		for(;;) {
			startIndex = text.indexOf("title=\"DOI\"", startIndex); //find the DOI field
			if(startIndex < 0) //end if there aren't any more DOIs on this page
				break;
			startIndex += 20; //skip past the numbers to find the unique DOI number
			endIndex = text.indexOf('<', startIndex); //find the terminating <
			String doiText = text.substring(startIndex, endIndex); //get the valid number
			doiText = doiText.trim(); //trim the number in case of extra spaces
			if(!visited.contains(doiText)){
				visited.add(doiText);
				q.add(doiText); //add them to the queue and the visited set if they have not been crawled previously
			}
		}
	}
	
	//crawls the IEEE Xplore DL, starting at each of the seeds. Note that each seed should be from a different conference/journal
	public void crawlIEEE(ArrayList<String> seeds) throws Exception { 
		String graphData = ""; //String for reducing File I/O cost
		HashSet<String> visited = new HashSet<>(); //visited set
		Queue<String> q = new LinkedList<>(); //queue for BFS
		String currentText = null; //placeholder for the current text
		for(int i = 0; i < seeds.size(); i++)
			seeds.set(i, "/document/" + seeds.get(i)); //add the necessary /document prefix
		q.addAll(seeds);
		visited.addAll(seeds); //add the seed to both places
		while(!q.isEmpty()) {
			String doi = q.poll(); //pop the top
			currentText = getIEEEText(doi); //get the text
			graphData += "\n" + getIEEETitle(currentText) + "\n";
			graphData += getIEEEConference(currentText) + "\n";
			graphData += getIEEEJournal(currentText) + "\n"; //get all the necessary text
			graphData += getIEEEDate(currentText) + "\n";
			graphData += getIEEEAbstract(currentText) + "\n";
			graphData += getIEEEKeywords(currentText).toString();
			addIEEELinks(currentText, visited, q); //add the other papers of the conference/journal to the queue/visited
		}
		outputPW.println((visited.size() - extraLinksVisited) + graphData); //print the results
		outputPW.close();
	}
	
	//returns the HTML text from the IEEE doi
	public String getIEEEText(String doi) throws Exception {
		String text = getURLText(IEEE_BASE_URL + doi + "/");
		return text;
	}
	
	 //returns the title from an IEEE page
	private String getIEEETitle(String text) {
		int tiIndex = text.indexOf("ArticleTitle")+ 15; //find the title field 
		int tiEndIndex = text.indexOf("\",", tiIndex); //find the terminating quote
		String tiText = text.substring(tiIndex, tiEndIndex); //get the title
		tiText = getProcessedText(tiText); //replace invalid stuff
		return tiText;
	}
	
	//returns the conference from an IEEE page if applicable. Note that this functionality is not currently relevant in the crawler
	private String getIEEEConference(String text) { 
		int coStartIndex = text.indexOf("isConference") + 14; //find the isConference field
		int coEndIndex = text.indexOf(',', coStartIndex); //find the terminating comma
		String isConf = text.substring(coStartIndex, coEndIndex); //get the boolean value
		if(isConf.equals("false"))
			return "None";  //exit if this was not in a conference
		
		coStartIndex = text.indexOf("publicationTitle") + 19; //find the title field
		coEndIndex = text.indexOf('\"', coStartIndex); //find the terminating quote
		String coText = text.substring(coStartIndex, coEndIndex); //get the conference title		
		coText = getProcessedText(coText); //replace invalid stuff
		return coText;
	}
	
	//returns the journal of an IEEE page if applicable. Note that this functionality is not currently relevant in the crawler
	private String getIEEEJournal(String text) { 
		int joStartIndex = text.indexOf("isJournal") + 11; //find the isJournal field
		int joEndIndex = text.indexOf(',', joStartIndex); //find the terminating comma
		String isJourn = text.substring(joStartIndex, joEndIndex); //get the boolean value
		if(isJourn.equals("false")) 
			return "None"; //exit if this was not in a journal
		
		joStartIndex = text.indexOf("publicationTitle") + 19; //find the title field 
		joEndIndex = text.indexOf('\"', joStartIndex); //find the terminating quote
		String joText = text.substring(joStartIndex, joEndIndex); //get the journal title
		
		joStartIndex = text.indexOf("\"volume\"", joStartIndex) + 10; //find the volume field and skip to the relevant part
		joEndIndex = text.indexOf('\"', joStartIndex); //find the terminating quote
		joText += " VOLUME " + text.substring(joStartIndex, joEndIndex); //get the volume and add it on
		
		joStartIndex = text.indexOf("\"issue\"", joStartIndex) + 9; //find the issue field and skip to the relevant part
		joEndIndex = text.indexOf('\"', joStartIndex); //find the terminating quote
		joText += " ISSUE " + text.substring(joStartIndex, joEndIndex); //get the issue and add it on
		
		joText = getProcessedText(joText); //replace invalid stuff
		return joText;
	}
	
	//returns the publication date of an IEEE article, trying various dates if necessary
	private String getIEEEDate(String text) { 
		int daStartIndex = text.indexOf("\"publicationDate\""); //find the date field
		if(daStartIndex < 0) 
			daStartIndex = text.indexOf("DateOfPublication") + 20; //get other publication date field if necessary
		else
			daStartIndex += 19; //otherwise advance to the necessary part
		int daEndIndex = text.indexOf('\"', daStartIndex); //find the terminating quote
		String daText = text.substring(daStartIndex, daEndIndex); //get the date
		String[] split = daText.split(" ");
		daText = split[split.length - 1]; //extract only the year
		daText = getProcessedText(daText); //replace invalid stuff
		return daText;
	}
	
	//returns the abstract text from an IEEE page
	private String getIEEEAbstract(String text) { 
		int startAbIndex = text.indexOf("\"abstract\"") + 12; //find the abstract field
		int endAbIndex = text.indexOf("\",", startAbIndex); //find ending quote
		String abText = text.substring(startAbIndex, endAbIndex); //get the abstract text
		abText = getProcessedText(abText).toLowerCase(); //replace invalid stuff and make it lowercase
		return abText;
	}
	
	//returns all of the keywords from an IEEE page
	private HashSet<String> getIEEEKeywords(String text) { 
		HashSet<String> keywordList = new HashSet<>(); //use HashSet to eliminate duplicates
		int startIndex = text.indexOf("\"keywords\"") + 12; //find the keywords area
		int lastIndex = text.indexOf("]}]", startIndex); //store the end of this relevant zone
		int endIndex = 0; //init the end index
		for(;;) {
			startIndex = text.indexOf('[', startIndex); //get the start of the list
			if(startIndex > lastIndex) //end if we left the zone
				break;
			startIndex++; //increment the index past the brace
			endIndex = text.indexOf(']', startIndex); //find the end of the list
			String terms = text.substring(startIndex, endIndex); //get the term list
			String[] termList = terms.split(","); //separate the list by commas
			for(int i = 0; i < termList.length; i++) {
				String s = termList[i];
				s = getProcessedText(s).toLowerCase(); //replace invalid stuff and make it lowercase
				char c = s.charAt(0);
				if(c == '\"')
					s = s.substring(1); //take off quotes at the beginning
				if(s.isEmpty()) //don't add empty strings to be safe
					continue;
				c = s.charAt(s.length() - 1);
				if(c == '\"')
					s = s.substring(0, s.length() - 1); //take off quotes at the end
				if(s.isEmpty()) //don't add empty strings to be safe
					continue;
				keywordList.add(s);
			}
		}
		return keywordList;
	}
	
	//adds the DOIs from the Table of Contents of the journal/conference from an ACM page to the visited set and the queue
	private void addIEEELinks(String text, HashSet<String> visited, Queue<String> q) throws Exception { 
		int conStartIndex = text.indexOf("publicationNumber") + 20; //find the publication number
		int conEndIndex = text.indexOf('\"', conStartIndex); //find the terminating quote
		String pubNum = text.substring(conStartIndex, conEndIndex); //get the publication number
		String endURL = "/xpl/mostRecentIssue.jsp?punumber=" + pubNum; //store end URL
		String secondText = "";
		if(!visited.contains(endURL)) {
			visited.add(endURL); //add the link to the visited to ensure that we do not go to unnecessary links
			secondText = getURLText(IEEE_BASE_URL + endURL); //go to the conference/journal page to find the links
			extraLinksVisited++;
		}
		else
			return; //otherwise quit if we have already gone here
		
		int dispIndex = secondText.indexOf("class=\"results-display\""); //find the display area
		conStartIndex = secondText.indexOf("of", dispIndex) + 2; //find the total number of pages to display
		conEndIndex = secondText.indexOf("</div>", conStartIndex); //find the terminating div tag
		String dispNum = secondText.substring(conStartIndex, conEndIndex); //get the number + spaces, etc.
		dispNum = getProcessedText(dispNum); //clean up the number
		endURL += "&rowsPerPage=" + dispNum; //update end URL
		String newText = "";
		if(!visited.contains(endURL)) {
			visited.add(endURL); //add the link to the visited to ensure that we do not go to unnecessary links
			newText = getURLText(IEEE_BASE_URL + endURL); //get the full list of links
			extraLinksVisited++;
		}
		
		int startIndex = 0, endIndex = 0; 
		for(;;) {
			startIndex = newText.indexOf("href=\"/document", startIndex); //find the link field
			if(startIndex < 0) //end if there aren't any more links
				break;
			startIndex += 16; //skip to the number part
			endIndex = newText.indexOf('/', startIndex); //find the terminating /
			String doiText = "/document/" + newText.substring(startIndex, endIndex); //get the number
			doiText = doiText.trim(); //trim the text
			if(!visited.contains(doiText)){
				visited.add(doiText);
				q.add(doiText); //add them to the visited set and the queue if they have not been crawled yet
			}
		}
	}
}
