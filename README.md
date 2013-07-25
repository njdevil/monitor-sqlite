monitor-sqlite v3.1
==============

Python (WSGI) & Django Server Health/Activity Monitor

##Database##
WSGI version is coded to use Sqlite3

##Procedure##
###Record Store###
recordstore-sqlite.py is called every X minutes via a Cronjob.
Data is parsed from the output of "top" to obtain the current System Load and Used Memory
The number of lines are counted from all of the /var/log/apache2/*/access.log files to get a clear picture of the number of requests that the Apache server is receiving.
Checking these requests by File Size is ineffective due to varying lengths of User-Agent strings.  Whereas, each request takes up 1 line.  There is NO logic for combining requests from the same visitor.

These 3 values are written to the Database.

###Record Display###
When calling the WSGI script or the Django View, the data is retrieved and reformatted into the structure required by the new Google Charts Javascript format
This data is then rendered through their Annotated Line Chart (with dates) and displayed on screen.
Record display is limited to 100,000 data points, but can be removed since Google Charts does not impose a limit (it will just take a really long time)


GPL
-----------
This code is released as GPL3 and is copyright 2013 by Modular Programming Systems Inc.
