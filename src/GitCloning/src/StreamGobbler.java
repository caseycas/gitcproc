import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

/**
 * 
 * StreamGobbler class credited to:
 * http://www.javaworld.com/article/2071275/core-java/when-runtime-exec---won-t.html?page=2
 *
 */
public class StreamGobbler extends Thread
{
	InputStream is;
	String type;
	boolean hasOutput;

	StreamGobbler(InputStream is, String type)
	{
		this.is = is;
		this.type = type;
		hasOutput = false;
	}

	public void run()
	{
		try
		{
			InputStreamReader isr = new InputStreamReader(is);
			BufferedReader br = new BufferedReader(isr);
			String line=null;
			while ( (line = br.readLine()) != null)
			{
				hasOutput=true;
				System.out.println(type + ">" + line);   
			}
		} catch (IOException ioe)
		{
			ioe.printStackTrace();  
		}
	}
}

