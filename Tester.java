/**
* A tester class for the ResearchCrawler. It contains many instances of the ResearchCrawler object,
* which are used to crawl the digital libraries.
* @author Luke Schoeberle
*/

import java.util.ArrayList;
import java.util.Arrays;

public class Tester {
	
	/**
	 * A tester function, which contains two sample timed runs. The IEEE one has already been completed, but the ACM one needs to be completed.
	 * Note that you will need to find the DOIs if you will run this on other conferences. See the format of these runs for more information on that.
	 * @param args Irrelevant
	 * @throws Exception Possible HTTP errors (should only occur on the server's end)
	 */
	public static void main(String[] args) throws Exception {
		long time = System.currentTimeMillis();
		
//		ResearchCrawler rc12 = new ResearchCrawler(".\\IEEE-ASE.txt");
//		rc12.crawlIEEE(new ArrayList<>(Arrays.asList("632827","732596","802342","873656","989853","1114992","1240314","1342757","4019556","4639314","5431781","6100050","6494914","6693069","7371998","7582760","8115615")));
//		System.out.println("Finished ASE in " + (System.currentTimeMillis() - time) / 60000.0 + " minutes!"); //print time in minutes
//		time = System.currentTimeMillis();		
		
		ResearchCrawler rc = new ResearchCrawler(".\\outputs\\ACM-KDD.txt"); //TODO
		rc.crawlACM(new ArrayList<>(Arrays.asList("312129.312167", "347090.347091", "502512.502513", "775047.775049", "956750.956752", "1014052.1014053", "1081870.1081871", "1150402.1150404", "1281192.1281193","1401890.1401891","1557019.1557021","1835804.1835805","2020408.2020410","2339530.2378371","2487575.2492148","2623330.2630816","2783258.2785464","2939672.2945357","3097983.3105807")));
		System.out.println("Finished KDD in " + (System.currentTimeMillis() - time) / 60000.0 + " minutes!"); //print time in minutes
		time = System.currentTimeMillis();	
	}
}
