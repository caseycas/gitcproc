#Constants for the keywords
SINGLE = "single"
BLOCK = "block"
INCLUDED = "included"
EXCLUDED = "excluded"

KEYLISTSIZE = 3

#Constants for which phase we are in
LOOKFORNAME = 1
LOOKFOREND = 2
LOOKFOREXCP = 3
LOOKFOREXCPEND = 4

#LineTypes
ADD = 1
REMOVE = 2
OTHER = 3

#Scope Change directions
INCREASE = 1
DECREASE = 2

#Comment Change Markers
UNMARKED = 0
UNCHANGED = 1
COMADD = 2
COMDEL = 3
TOTALADD = 4
TOTALDEL = 5

#Label for structures found outside of a function
MOCK = "NO_FUNC_CONTEXT"