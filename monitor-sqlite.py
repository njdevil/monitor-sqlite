import commands
import datetime
import os
import re
import sqlite3

DATABASE_FILE='/root/monitor.db'
DATABASE_TABLE='records'

def checkdb():
    if not os.path.exists(DATABASE_FILE):
        dbconn=sqlite3.connect(DATABASE_FILE)
        query=dbconn.cursor()
        query.execute('create table records (command text, date real, time real, value real)')
        dbconn.commit()
        dbconn.close()


def dates():
    date=(datetime.datetime.now()).strftime("%Y%m%d")
    time=(datetime.datetime.now()).strftime("%H%M")
    return date,time


def dbinsert(command,value,table=DATABASE_TABLE):
    date,time=dates()
    dbconn=sqlite3.connect('/root/monitor.db')
    insert=dbconn.cursor()
    insert.execute('insert into '+table+' values("'+command+',"'+date+'","'+time+'","'+value+'")')


def getapachewc():
    for a,b,c in os.walk('/var/log/apache2'):
        for file in c:
            data=""
            if not re.search("mpsclient",a) and not re.search("alpha",a):
                if re.search("access\.log$",file):
                    data=commands.getoutput("wc -l "+os.path.join(a,file))
                    data=re.sub(" .*$","",data)
                    count.append(int(data))
    dbinsert('wc',str(sum(count)))


def getloadmem():
    topdata=commands.getoutput("top -b -n 1")
    topdatasplit=topdata.split("\n")
    load=topdatasplit[0]
    memory=topdatasplit[3]
    processload(load)
    processmem(memory)


def processload(load):
    load=re.sub("^.*load average: ","",load)
    load=re.sub(",.*","",load)
    load=float(load)
    load=str(load*100)
    dbinsert('load',load)


def processmem(memory):
    memory=re.sub("^.*total,","",memory)
    memory=re.sub("k used,.*","",memory)
    memory=re.sub("\s","",memory)
    memory=float(memory)
    memory=str(round(memory/1000,0))
    dbinsert('memory',memory)


if __name__=="__main__":
    checkdb()
    getloadmem()
    getapachewc()
    
