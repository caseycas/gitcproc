# GitCProc
GitCProc is a tool to extract changes to elements in code and associate them with their surrounding functions.
It takes git diff logs as input and produces a table mapping the additions and deletions of the elements to
a 4-tuple (project, sha, file, function/method) specifying the commit and location in the code of changed elements.
It also analyzes commit messages to estimate if the commits were bug fixing or not.

Currently, we have designed it to work with C/C++/Java, but it will likely work for languages with similar 
functional/method structure that use { ... } to enclose blocks.

#Required Libraries
GitCProc runs on python 2.7 and requires the following libraries:
-psycopg2
-nltk

If you wish to output your results to a database instead of a csv file, you will need a postgres server installed.

#Running Instructions

The tool works by parsing git log files produced with the -W (function-content ) to the tool along with a few other options
specified in either util.py or a config.ini file.  The util.py file specifies whether to output to csv or database, record
debug information, and points to the config.ini file.  The config.ini file specifies the tables in the database (currently
must be created manually before) and the location of the keywords file.

The keywords file specifies what structures you wish to track.  It is formatted in the following manner:
<br/>
[keyword_1], [INCLUDED/EXCLUDED], [SINGLE/BLOCK]
<br/>
...
<br/>
[keyword_N],[INCLUDED/EXCLUDED], [SINGLE/BLOCK]

The first part is the keyword you wish to track.  For instance, if you are tracking assert statements, one 
keyword of interest would be "assert", if you were tracking try-catch blocks, you might have "try" and "catch".
The second part specifies whether the keyword is being searched for (INCLUDED) or specifically ignored (EXCLUDED).
For example, if you are tracking assertions, but you wish to exclude headers, you would have a line like
"assert.h,EXCLUDED,SINGLE".  The last part specifies whether the keyword refers to a single line coding element or
a multiple line element.  A single line element might be "println", where as "for" with a BLOCK designation will
track all the contents of the for loop encased by {...}.

python ghProc.py [git_log]

#Running Tests

There are currently two test scripts, which can be run as:
python logChunkTest.py (Tests 2, 13, 23, 31, 36 fail)
python ghLogDbTest.py (Tests 4 and 7)

The failing tests are the result of not currently supporting the tracking of deleted functions.

#Performance
Updated soon...

#Upcoming Features
* Handling of deleted functions
* Automated download of repositories from Github and log creation
* Better authorship recording (author + committer)
* Output of line contents and not just counts of lines changed.
* ...
