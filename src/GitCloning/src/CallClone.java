import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.Scanner;

import javax.net.ssl.HttpsURLConnection;

import org.apache.commons.io.IOUtils;

public class CallClone {

	//public static String cloningDirectory = "/Archive/2/ghmineProjects7/";
	public static String cloningDirectory;
	
	public static String getProjectURL(String baseURL)
	{
		//Do some validation on the name
		if(!baseURL.matches(".*/.*"))
		{
			throw new IllegalArgumentException("A project name doesn't match the expected design.");
		}
		return "https://github.com/" + baseURL.trim();
	}
	
	public static String getCloneURL(String baseURL)
	{
		if(!baseURL.matches(".*/.*"))
		{
			throw new IllegalArgumentException("A project name doesn't match the expected design.");
		}
		return "https://github.com/" + baseURL.trim() + ".git";
	}
	
	public static String repoDir(String base)
	{
		return base.replace("/", "___");
	}
	
	public static void main (String args[])
	{
		String inputfile = "";
		int start = 0;
		int end = 0;
		try
		{
			inputfile = args[0];
			cloningDirectory = args[1];
			start = Integer.parseInt(args[2]);
			end = Integer.parseInt(args[3]);
		}
		catch(Exception e)
		{
			System.out.println("Please enter the inputfile name, and the start and end indicies of");
			System.out.println("the repositories you wish to clone.");
			System.exit(-1);
		}
		
		System.out.println("Arguments read in.");
		
		//System.out.println(inputfile);
		//System.out.println(start);
		//System.out.println(end);
		//System.exit(-1);
		
		ArrayList<String> repoList = new ArrayList<String>();
		
		try {
			Scanner sc = new Scanner(new File(inputfile));
			int i = 0;
			while(sc.hasNextLine())
			{
				if(i < start)
				{
					i++;
					sc.nextLine();
				}
				else if(i > end)
				{
					break;
				}
				else
				{
				String repo = sc.nextLine();
				if(repo.startsWith("https://api.github.com/repos/"))
				{
					repo = repo.substring(29);
					System.out.println(repo);
				}
				repoList.add(repo);
				i++;
				}
			}
			sc.close();
			System.out.println("Loaded in List of Repos.");
			
			ArrayList<String> errorcases = new ArrayList<String>();
			ArrayList<String> missingProjects = new ArrayList<String>();
			ArrayList<String> otherMissing = new ArrayList<String>();
			i = 0;
			for (String repo : repoList)
			{
				System.out.println(i + ":" + repo);
				//System.exit(0);
				
				String nextURL = getProjectURL(repo);
				System.out.println("Number: " + i + " URL: " + nextURL);
				HttpsURLConnection connect = (HttpsURLConnection) new URL(nextURL).openConnection();
				connect.setRequestMethod("GET");
				try{
				connect.connect();
				int response = connect.getResponseCode();

				if(response!=404 && response!=403 && response!=409)
				{
					InputStream in = connect.getInputStream();
					String encoding = connect.getContentEncoding();
					encoding = encoding == null ? "UTF-8" : encoding;
					String body = IOUtils.toString(in, encoding);
					if(!body.contains("Repository unavailable due to DMCA takedown.") && !body.contains("This repository has been disabled."))
					{
					System.out.println(response);
					connect.disconnect();
					}
					else
					{
						System.out.println("Missing: " + repo);
						missingProjects.add(repo);
						connect.disconnect();
						continue; //Skip cloning of nonexisting repos.
					}
				}
				else
				{
					System.out.println("Missing: " + repo);
					missingProjects.add(repo);
					connect.disconnect();
					continue; //Skip cloning of nonexisting repos.
				}
				
				}
				catch(Exception e)
				{
					System.out.println("Other error: " + repo);
					otherMissing.add(repo);
					continue;
				}
				
				i++;
				String repoURL = getCloneURL(repo);
				System.out.println("git clone " + repoURL + " " + cloningDirectory + repoDir(repo));
				//System.exit(0);
				try {
					Process p = Runtime.getRuntime().exec("git clone " + repoURL + " " + cloningDirectory + repoDir(repo));
					//Make sure to remove any error or output buffers from this process to prevent hanging.
					StreamGobbler errorGobbler = new StreamGobbler(p.getErrorStream(), "out");
					StreamGobbler outputGobbler = new StreamGobbler(p.getInputStream(), "err");
					errorGobbler.start();
					outputGobbler.start();
					p.waitFor(); //Let this clone complete before moving to the next.
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
					errorcases.add(repoURL);
				}
				catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
					errorcases.add(repoURL);
				}
			}
			
			PrintWriter writer = new PrintWriter("CloneErrorCases.txt");
			System.out.println("Printing error cases");
			for(String errorRepo : errorcases)
			{
				writer.println(errorRepo);
			}
			writer.close();
			
			System.out.println("Printing missing repos.");
			writer = new PrintWriter("MissingGitRepos.txt");
			for(String nextRepo : missingProjects)
			{
				writer.println(nextRepo);
			}
			writer.close();
			
			System.out.println("Printing other URL errors");
			writer = new PrintWriter("OtherGitRepos.txt");
			for(String nextRepo : otherMissing)
			{
				writer.println(nextRepo);
			}
			writer.close();
			
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (MalformedURLException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		} catch (IOException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
	
	}
}
