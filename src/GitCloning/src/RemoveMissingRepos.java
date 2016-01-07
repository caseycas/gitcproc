import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.Scanner;

import javax.net.ssl.HttpsURLConnection;


/**
 * Some of the projects in the list I've noticed don't exist any longer.
 * Therefore, I am checking to see if the pages get a 404 and removing those
 * that do.
 * @author caseycas
 *
 */
public class RemoveMissingRepos {
	
	public static String convertURL(String baseURL)
	{
		//Do some validation on the name
		if(!baseURL.matches(".*/.*"))
		{
			throw new IllegalArgumentException("A project name doesn't match the expected design.");
		}
		return "https://github.com/" + baseURL.trim();
	}
	
	public static void main(String args[])
	{
		String inputfile = "";
		ArrayList<String> validProjects = new ArrayList<String>();
		ArrayList<String> missingProjects = new ArrayList<String>();
		ArrayList<String> otherMissing = new ArrayList<String>();
		try
		{
			inputfile = args[0];
		}
		catch(ArrayIndexOutOfBoundsException e)
		{
			System.out.println("Please enter the input file of URLs as a command line argument.");
			System.exit(-1);
		}
		Scanner sc;
		try {
			sc = new Scanner(new File(inputfile));
			int i = 0;
			while(sc.hasNextLine())
			{
				String baseURL = sc.nextLine();
				String nextURL = convertURL(baseURL);
				System.out.println("Number: " + i + " URL: " + nextURL);
				HttpsURLConnection connect = (HttpsURLConnection) new URL(nextURL).openConnection();
				connect.setRequestMethod("GET");
				try{
				connect.connect();
				int response = connect.getResponseCode();
				if(response!=404)
				{
					validProjects.add(baseURL);
				}
				else
				{
					System.out.println("Missing: " + baseURL);
					missingProjects.add(baseURL);
				}
				connect.disconnect();
				i++;
				}
				catch(Exception e)
				{
					System.out.println("Other error: " + baseURL);
					otherMissing.add(baseURL);
				}
			}
			
			sc.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (MalformedURLException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		//Write the new URLs out to file.
		try {
			PrintWriter writer = new PrintWriter("CleanedGitRepos.txt");
			for(String nextRepo : validProjects)
			{
				writer.println(nextRepo);
			}
			writer.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		//Write out the deleted projects to file.
		try {
			PrintWriter writer = new PrintWriter("MissingGitRepos.txt");
			for(String nextRepo : missingProjects)
			{
				writer.println(nextRepo);
			}
			writer.close();
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		//Write ones that were the result of other errors.
				try {
					PrintWriter writer = new PrintWriter("OtherGitRepos.txt");
					for(String nextRepo : otherMissing)
					{
						writer.println(nextRepo);
					}
					writer.close();
				} catch (FileNotFoundException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
		

	}
}
