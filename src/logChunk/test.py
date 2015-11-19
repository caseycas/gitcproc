# import re
#
# from string import maketrans
#
# text=open(r"C:\Users\Yagnik\PycharmProjects\logchunkexep\test.txt",'r').read()
#
# lst=['match1','match2','match3']
# count=0
# for l in text.split('\n'):
#     if any(s in l for s in lst):
#         count+=1
#
# print count
# # pattern="\w*Exception"
# # all= set(re.findall(pattern,text))
# #
# #
# # for x in all:
# #     print x
# #
# # for line in text.split('\n'):
# #     if re.search("\\w*Exception",line):
# #         print line


# import re
#
# pattern=" throw |\\bnull| return |[, \-!?:(){};+]+"
#
# text="return null;"
#
# x=filter(None, re.split(pattern, text))
# print x
#
# err_str=' error | bug | fix | issue | mistake | blunder | incorrect | fault | defect | flaw | glitch | gremlin '
# log='   Bugs fix'
# if re.search(err_str, log, re.IGNORECASE):
#     print "wololo"

line='	private void copy(inputstream is, outputstream os, int max) throws ioexception{'
keyword=['throw ', 'included', 'single']
if(keyword[0] in line.lower()):
    print "wololo"

functionPattern2 = " [\w\d:_]+&* *\** +[\w\W\d_:~]+&* *\([\w\W\d_,\[\]\*\(\)&:<>]*\) *{$"


line0='@Override public Loader<List<Gist>> onCreateLoader(int i, Bundle bundle) {'

line1=