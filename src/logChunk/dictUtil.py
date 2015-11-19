#Key, dictionary[key, int], int --> dictionary[key, int]
#Given a key, dictionary and increment, set the dictionary value at
#key to dictionary[key] + inc. If there is no old value, set to inc
def incrementDict(dictKey, dictionary, inc=1):
	if(dictKey in dictionary):
		dictionary[dictKey] += inc
	else:
		dictionary[dictKey] = inc

	return dictionary

#dictionary[key, int] -> boolean
#Given a dictionary of counts return true if at least one is non zero
#and false otherwise
def nonZeroCount(dictionary):
	for k,v in dictionary.iteritems():
		assert(v >= 0)
		if(v > 0):
			return True

	return False