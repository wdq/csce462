import java.net. *;
import java.io. *;

//
// File: url.java
// Modified by: Byrav Ramamurthy (byrav@cse.unl.edu)
// Date: September 28, 1998
//
// Implements: OpenStreamTest class
// Input: Name of a web address (URL)
// Output: Text contents of the webpage
//
//
//
//
// To compile:
//      javac url.java
// To run:
//      java OpenStreamTest
//

class url2 {
	public static void main(String[] args) {
		try {
			String url;
			System.out.println("Enter the URL: ");
			BufferedReader f = new BufferedReader(new InputStreamReader(System.in));
			url=f.readLine();
			URL yahoo = new URL(url);
			URLConnection yahoo1=yahoo.openConnection();
			int len = yahoo1.getContentLength();
			if(len <= 0) { // Something with SSL may be bad if no content...
				if(url.toLowerCase().contains("http:/")) { // Just toggle http/https
					url = url.replace("http:/", "https:/");
				} else if(url.toLowerCase().contains("https:/")) {
					url = url.replace("https:/", "http:/");
				}
				// Retry the connection
				yahoo = new URL(url);
				yahoo1 = yahoo.openConnection();
			}
			InputStreamReader inputStreamReader = new InputStreamReader(yahoo1.getInputStream());
			BufferedReader dis = new BufferedReader(inputStreamReader);
			String inputLine;

		while ((inputLine = dis.readLine()) != null) {
			System.out.println(inputLine);
		}
		dis.close();
		} catch (MalformedURLException me) {
			System.out.println("MalformedURLException: " + me);
		} catch (IOException ioe) {
			System.out.println("IOException: " + ioe);
		}
	}
}

