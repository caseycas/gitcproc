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


	public static String cloningDirectory;
	public static String Separator = "___";
	public static final String validLogin = "[\\w\\-]*";
	public static final String validProject = "[\\w\\-\\.]*";
	public static final String ghAPIURLbase1 = "https://api.github.com/repos/";
	public static final String ghAPIURLbase2 = "https://www.api.github.com/repos/";
	public static final String ghURLbase1 = "https://github.com/";
	public static final String ghURLbase2 = "https://www.github.com/";
	
	
	public static String getBase(String repo)
	{
		if(repo.contains(ghAPIURLbase1))
		{
			repo = repo.replace(ghAPIURLbase1, "");
		}
		else if (repo.contains(ghAPIURLbase2))
		{
			repo = repo.replace(ghAPIURLbase2, "");
		}
		else if (repo.contains(ghURLbase1))
		{
			repo = repo.replace(ghURLbase1, "");
		}
		else if (repo.contains(ghURLbase2))
		{
			repo = repo.replace(ghURLbase2, "");
		}
		return repo;
	}
	
	public static String getProjectURL(String baseURL)
	{		
		//Do some validation on the name
		if(baseURL.matches(validLogin + "/" + validProject))
		{
			return "https://github.com/" + baseURL.trim();
		}
		else
		{
			throw new IllegalArgumentException("A project name doesn't match the expected input format.");
		}
		
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
		return base.replace("/", Separator);
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
			if(args.length == 5)
			{
				CallClone.Separator = args[4];
			}
		}
		catch(Exception e)
		{
			System.out.println("Please enter the inputfile name, and the start and end indicies of");
			System.out.println("the repositories you wish to clone.");
			System.out.println("Also takes in an optional final argument to change the separator.");
			System.exit(-1);
		}
		
		System.out.println("Arguments read in.");
		
		
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

				repoList.add(getBase(repo));
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
				String nextURL = "";
				try
				{
				nextURL = getProjectURL(repo);
				}
				catch(IllegalArgumentException e)
				{
					System.out.println("Invalid Repo Name: " + repo);
					otherMissing.add(repo);
					i++;
					continue;
				}
				System.out.println("Number: " + i + " URL: " + nextURL);
				i++;
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
