import static org.junit.Assert.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

import org.junit.Test;

public class NameValidationTests {

	@Test
	public void testNameValidation() {
		Scanner sc = null;
		try {
			sc = new Scanner(new File("GHNames.txt"));
		} catch (FileNotFoundException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		int i = 0;
		while(sc.hasNextLine())
		{
			System.out.println(i);
			i++;
			String repo = sc.nextLine();
			repo = CallClone.getBase(repo);
			try
			{
			CallClone.getProjectURL(repo);
			}
			catch(IllegalArgumentException e)
			{
				assertTrue(false);
			}
		}
	}

}
