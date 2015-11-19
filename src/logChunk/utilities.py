#This is harder than I thought.  Problem is that the function names can span 
#multiple lines and include additions and deletions.

#So, in the case of an NA, we likely need to create a new object to hold the whole string
#up to the next chunk.
#Then divide up for each method in chunk and create separate row for that.

#string -> string
#if this is a chunk with a method name in it, try to extract the method name.
def isMethodLine(line):
    