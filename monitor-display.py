#! /usr/bin/python

import commands
import datetime
import re
import sqlite3
import time

dbconn=sqlite3.connect('/var/www/hosts/assets.usatoday.com/code/monitor.db', check_same_thread = False)
def dbquery(querystring):
    query=dbconn.cursor()
    query.execute(querystring)
    queryout=query.fetchall()
    return queryout


def createYaxis(command):
    if command=="memory":
        tempdata=""
        tempdata+='<div id="memory">\n<img src="http://chart.apis.google.com/chart?cht=lc&chs=33x235&chd=t:0,0,0&chxt=y&chxr=0,500,1052,69&chds=500,1052"></div>'
        yaxisvals=["500","1052","69"]

    else:
        tempdata=""
        date6=(datetime.datetime.now()-datetime.timedelta(days=6)-datetime.timedelta(hours=5)).strftime("%Y%m%d")
        value=[]
        query=dbquery('select * from records where date>='+date6+' and command="'+command+'"')
        for item in query:
            value.append(int(item[3]))

        maxval=max(value)
        minval=min(value)

        if command=="wc":
            minval=0
        if (maxval-minval)%8 != 0:
            maxval=maxval+(8-(maxval-minval)%8)

        yaxisvals=[]
        yaxisvals.append(str(minval))
        yaxisvals.append(str(maxval))
        yaxisvals.append(str((maxval+minval)/8.0))
        if command=="load":
            tempdata+='<div id="'+command+'">\n<img src="http://chart.apis.google.com/chart?cht=lc&chs=22x235&chd=t:0,0,0&chxt=y&chxr=0,'+yaxisvals[0]+','+yaxisvals[1]+','+yaxisvals[2]+'&chds='+yaxisvals[0]+','+yaxisvals[1]+'"></div>'
        else:
            tempdata+='<div id="'+command+'">\n<img src="http://chart.apis.google.com/chart?cht=lc&chs=28x235&chd=t:0,0,0&chxt=y&chxr=0,'+yaxisvals[0]+','+yaxisvals[1]+','+yaxisvals[2]+'&chds='+yaxisvals[0]+','+yaxisvals[1]+'"></div>'

    return tempdata,yaxisvals


def determineTZ():
    dst=commands.getoutput("date")
    if re.search("E.T",dst):
        dst=re.sub("^.*E","E",dst)
        dst=re.sub("T.*","T",dst)
        if dst=="EDT":
            timetemp=datetime.datetime.utcnow()-datetime.timedelta(hours=4)
        if dst=="EST":
            timetemp=datetime.datetime.utcnow()-datetime.timedelta(hours=5)
    if re.search("America",dst):
        timetemp=datetime.datetime.utcnow()-datetime.timedelta(hours=5)
    else:
                timetemp=datetime.datetime.utcnow()-datetime.timedelta(hours=4)
    converttime=timetemp.strftime("%Y%m%d")
    converttimehr=int(timetemp.strftime("%H"))
    return converttime,converttimehr


def createXgrid(hours,hm):
    hourminlist=[float("%.3f" % ((i+4)/hm)) for i in range(0,24,4)]   #truncate for to limit google GET url size
    grid="&chm="
    for i in range(hours/4):
        grid+="R,dddddd,0,"+str(hourminlist[i]-.001)+","+str(hourminlist[i]+.002)
        if i!=range(hours/4)[-1]:
            grid+="|"
    return grid



def xaxis(date,command):
    hours=width=xaxislist=converttime=converttimehr=minutes=hm=grid=hm4=hm8=hm12=hm16=hm20=""
    converttime,converttimehr=determineTZ()
    if date==converttime:
        hours=converttimehr
        minutes=int(datetime.datetime.utcnow().strftime("%M"))
        width=int(((60*hours)+minutes)/7)
        hm=hours+(minutes/60.0)
        grid=createXgrid(hours,hm)
    else:
        hours=24
        hm=24.0
        width=205
        grid=createXgrid(hours,hm)

    return hours,width,grid


def chart(command,daterange):
    tempdata,yaxisvals=createYaxis(command)

    for dateitem in daterange:
        i=0
        numberstring=""
        numbers=[]
        query=dbquery('select * from records where date='+dateitem[1]+' and command="'+command+'" order by time')
        print query
        for item in query:
            i+=1
            numbers.append(float(item[3]))
            if i!=1:
                numberstring+=","+str(item[3])
            else:
                numberstring+=str(item[3])
        if not numbers:
            numbers=[0]

        hours,width,grid=xaxis(dateitem[1],command)
        tempdata+='<div id="'+dateitem[0]+''+command+'">\n<img src="http://chart.apis.google.com/chart?cht=lc&chs='+str(width)+'x225&chd=t:'
        tempdata+=numberstring
        tempdata+="&chds="+yaxisvals[0]+","+yaxisvals[1]+grid+"&chg=0,25"
        tempdata+='"></div>\n'

    return tempdata


def chartheaders(commandlist,daterange):
    tempdata=""
    for item in daterange:
        tempdata+='<div id="'+item[0]+'">'+item[1]+'</div>\n'
    for command in commandlist:
        if command=="load":
            tempdata+='<div id="'+command+'name">'+command+'<br>x10<sup>-2</sup></div>\n'
        else:
            tempdata+='<div id="'+command+'name">'+command+'</div>\n'
    return tempdata


def dates():
    dates=dbquery('select distinct date from records order by date desc limit 7')
    daterange=[]
    for x in range(7):
        temp=[]
        temp.append("day"+str(x))
        temp.append(str(dates[x][0]))
        daterange.append(temp)
        daterange.reverse()
    return daterange


def html():
    outputdata=""
    outputdata+="""<html>
<head>
<style>
body {background-color: #bbbbbb;
        font-family: verdana;
        font-size: 120%;}
#loadname {position: absolute;
        top: 5px;
        margin-left: 0px;}
#load {position: absolute;
    top: 76px;
    margin-left: 0px;}
#memoryname {position: absolute;
        top: 350px;
        margin-left: 0px;}
#memory {position: absolute;
    top: 386px;
    margin-left: 0px;}
#wcname {position: absolute;
        top: 661px;
        margin-left: 0px;}
#wc {position: absolute;
    top: 696px;
    margin-left: 0px;}
#day0 {position: absolute;
    left: 50%;
    margin-left: 365px;}
#day1 {position: absolute;
    left: 50%;
    margin-left: 162px;}
#day2 {position: absolute;
    left: 50%;
    margin-left: -40px;}
#day3 {position: absolute;
    left: 50%;
    margin-left: -243px;}
#day4 {position: absolute;
    left: 50%;
    margin-left: -445px;}
#day5 {position: absolute;
    left: 50%;
    margin-left: -648px;}
#day6 {position: absolute;
    left: 50%;
    margin-left: -850px;}
#day0load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 1275px;}
#day1load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 1070px;}
#day2load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 865px;}
#day3load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 660px;}
#day4load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 455px;}
#day5load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 250px;}
#day6load {position: absolute;
    left: 0;
    top: 80px;
    margin-left: 45px;}
#day0memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 1275px;}
#day1memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 1070px;}
#day2memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 865px;}
#day3memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 660px;}
#day4memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 455px;}
#day5memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 250px;}
#day6memory {position: absolute;
    left: 0;
    top: 390px;
    margin-left: 45px;}
#day0wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 1275px;}
#day1wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 1070px;}
#day2wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 865px;}
#day3wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 660px;}
#day4wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 455px;}
#day5wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 250px;}
#day6wc {position: absolute;
    left: 0;
    top: 700px;
    margin-left: 45px;}
</style>
</head>
<body>
"""
    return outputdata


def application(environ, start_response):
    status = '200 OK'

    response_headers = [('Content-type', 'text/html'),]
    start_response(status, response_headers)

    data=""

    commandlist=['load','memory','wc']

    daterange=dates()
    data=html()
    data+=chartheaders(commandlist,daterange)

    for command in commandlist:
        data+=chart(command,daterange)

    date=""
    data+="""</body>
</html>"""

    return [data]

if __name__=="__main__":
    try:
        import sys
        if sys.argv[0]:
            pass
    except:
        application()
    data=""

    commandlist=['load','memory','wc']

    daterange=dates()
    print daterange
    data=html()
    data+=chartheaders(commandlist,daterange)

    for command in commandlist:
        data+=chart(command,daterange)

    date=""
    data+="""</body>
</html>"""


