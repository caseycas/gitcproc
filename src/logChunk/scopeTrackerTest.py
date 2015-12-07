import unittest
import scopeTracker
from chunkingConstants import *

class logChunktest(unittest.TestCase):

	def setUp(self):
		self.sT = scopeTracker.scopeTracker("C")

	def test_scopeOrder(self):
		line = "} catch(Exception e) {"
		output = self.sT.scopeOrder(line)
		expected = [DECREASE, INCREASE]
		self.assertTrue(output == expected, "Test 1 Actual: " + str(output))

		line = "namespace temp { func A(int x) { if (x == 1) {return 0;} else {return 1;} } }"
		output = self.sT.scopeOrder(line)
		expected = [INCREASE, INCREASE, INCREASE, DECREASE, INCREASE, DECREASE, DECREASE, DECREASE]
		self.assertTrue(output == expected, "Test 2 Actual: " + str(output) )

		line = "namespace temp { func A(int x) { "
		output = self.sT.scopeOrder(line)
		expected = [INCREASE, INCREASE]
		self.assertTrue(output == expected, "Test 3 Actual: " + str(output))

		line = "}"
		output = self.sT.scopeOrder(line)
		expected = [DECREASE]
		self.assertTrue(output == expected, "Test 4 Actual: " + str(output))

		line = "blah {}}"
		output = self.sT.scopeOrder(line)
		expected = [INCREASE, DECREASE, DECREASE]
		self.assertTrue(output == expected, "Test 5 Actual: " + str(output))

		line = "x = y;"
		output = self.sT.scopeOrder(line)
		expected = []
		self.assertTrue(output == expected, "Test 6 Actual: " + str(output))


if __name__=="__main__":
    unittest.main()