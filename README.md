# GitCProc
GitCProc is a tool to extract changes to elements in code and associate them with their surrounding functions.
It takes git diff logs as input and produces a table mapping the additions and deletions of the elements to
a 4-tuple (project, sha, file, function/method) specifying the commit and location in the code of changed elements.
It also analyzes commit messages to estimate if the commits were bug fixing or not.

Currently, we have designed it to work with C/C++/Java/Python, but we have designed the framework to be extensible to other languages that make use of the concept of scope and source blocks.

# Video Demo

There is a video walkthrough of running the tool on a simple example at: https://youtu.be/shugzDjxj0w
A shortened version can be found here: https://youtu.be/5sOUoMHuP9s

# Walkthrough

There is also a text version of the video walkthrough in the file "ExampleWalkthrough".

# Docker

A docker to handle the installation of these libraries and install postgres can be obtained
with:

```
docker pull caseycas/gitcproc-docker
docker tag caseycas/gitcproc-docker gitcproc-docker
docker run --name gitcproc-docker -e POSTGRES_PASSWORD=postgres -d gitcproc-docker
docker exec -it gitcproc-docker bash
```

An example project and search can be run in the docker with (password prompt needs 'postgres'):
This should take about a minute to run.

```
cd src/logChunk/
python gitcproc.py -d -pl -wl ../util/docker_conf.ini
psql -U postgres
SELECT * FROM public.change_summary limit 5;
SELECT * FROM public.method_change_detail limit 5;
```

# Required Libraries
GitCProc runs on python 2.7 and requires the following libraries:
-psycopg2
-nltk
-PyYAML
-GitPython

The python script src/logChunk/installDependencies.py will install these for you.  Be aware that psycopg2 requires postgres to be installed on your machine with necessary supporting libraries.  For Ubuntu, make sure you have libpq-dev installed.

If you wish to output your results to a database instead of a csv file, you will need a postgres server installed.


# Running Instructions

The master script is located at src/logChunk/gitcproc.py, which depends on 3 input files to run.

1) First, if you want to download your projects from GitHub, you need a file to specify the list of projects
from GitHub.  The file format is a list of full project names, e.g. caseycas/gitcproc, one on each line.

2) The keywords file specifies what structures you wish to track.  It is formatted in the following manner:
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

If you want to exactly match a keyword, include "" around the keyword and it will match words where their is a
break in alphanumeric characters.  So "assert",INCLUDED,SINGLE would match assert(...), but not ASSERTTRUE(...).
If you want less exact matching, do not include quotations.

3) Finally, you need a config.ini file (several examples are included in src/util).
The sections of the config.ini file are as follows:

[Database]
- Here you list your database name, your user name, the host, port, schema, and the names for the two tables
created by the tool.  "table_method_detail" outputs information specific to changes to methods/functions, where
"table_change_summary" specifies information about each commit processed.

[Repos]
- Here you must specify your repo_url_file, which is described in 1) and the repo_locations:,
which is where you want to store your downloaded projects.

[Keywords]
- Here you must specify your keywords file, described in 2) under the option file:

[Log]
- This section has 1 option, languages:, where you specify which file types to include in the log,
currently, we support C, C++, Java, and Python file types.

[Flags]
- Finally, this section contains several output and debugging options:
	SEP: -> A string used to flatten out downloaded project names.  We recommend using ___ as we
	have not observed GitHub projects using this in their names.  To illustrate what it does, if
	this tool downloads caseycas/gitcproc with SEP: "___" the directory name it will be saved to
	is caseycas___gitcproc.
	DEBUG: -> True or False, this outputs extensive debug information.  It is highly recommended
	you set this to False when running on a real git project.
	DEBUGLITE: -> True or False, this outputs very lightweight debug information.
	DATABASE: -> True or False, this signals to write output to your Database.  The tool will
	create the tables if they don't exist yet, but you must have postgres installed will an
	available database and schema specified in [Database].  This option will prompt you for your
	database password once the script gitcproc.py starts.
    CSV: -> True or False, this signals to write to a CSV file. This option is recommended if you
    want to miminize set up and test the tool out.
	LOGTIME: -> True or False, this signals to write performance time information.  Currently it
	measure time to parse the log and time to write out to the Database or CSV file.

With these files created, to run the full process you can do something like:
python gitcproc.py -d -wl -pl ../util/sample_conf.ini

The config file is mandantory, and option -d runs the project download step,
-wl creates the git log for downloaded projects, and -pl parses the logs and
sends the output to your choosen format.


# Running Tests
This repository is set up to run travis CI on each commit at: https://travis-ci.org/caseycas/gitcproc

The test scripts are as follows
src/logChunk/logChunkTestC.py
src/logChunk/logChunkTestJAVA.py
src/logChunk/logChunkTestPython
src/logChunk/ghLogDbTest.py
src/logChunk/ghLogDbTestPython.py
src/logChunk/scopeTrackerTest.py

