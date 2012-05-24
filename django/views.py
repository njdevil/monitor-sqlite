from django.shortcuts import render_to_response
from PROJECT.APP.models import TABLE
import datetime

def chart(command):
        data="""<script type="text/javascript">
    google.load('visualization', '1', {packages: ['annotatedtimeline']});
    function drawVisualization() {
      var data = new google.visualization.DataTable();
      data.addColumn('datetime', 'Date');
      data.addColumn('number', '"""+command+"""');
      data.addRows(["""

	#for sanity reasons, 100k+ records takes a LONG time to process 
	queryout=TABLE.objects.filter(command=command).order_by('-date','time')[:10000]

        for i in queryout.values():
                if len(str(i['time']))==4:
                        temptime=i['time']
                if len(str(i['time']))==3:
                        temptime="0"+str(i['time'])
                if len(str(i['time']))==2:
                        temptime="00"+str(i['time'])
                if len(str(i['time']))==1:
                        temptime="000"+str(i['time'])
                tempdate=str(i['date'])+"-"+str(temptime)
                tempdate=datetime.datetime.strptime(tempdate, "%Y%m%d-%H%M").timetuple()
                tempdate=list(tempdate)
                tempdate[1]=tempdate[1]-1
                tempdate=tuple(tempdate)
                data+="[new Date"+str(tempdate[:6])+", "+str(i['value'])+"],\n"

        data+="""      ]);

      var annotatedtimeline = new google.visualization.AnnotatedTimeLine(
          document.getElementById('"""+command+"""'));
      annotatedtimeline.draw(data, {'displayAnnotations': true});
    }

    google.setOnLoadCallback(drawVisualization);
  </script>"""
        return data


def index(request):
    data=""
    commandlist=['load','memory','wc']
    for command in commandlist:
        data+=chart(command)
        if command=="load":
            data+='<div id="'+command+'name">System Load (as % of 1 processor)</div>'
        if command=="memory":
            data+='<div id="'+command+'name">System Used Memory (in MB)</div>'
        if command=="wc":
            data+='<div id="'+command+'name">"wc -l" Access Log File Size (in lines)</div>'
        data+='<div id="'+command+'" style="width: 1400px; height: 270px;"></div>'
        data+="<br>"
    data+="""</body>
</html>"""

    return render_to_response('servercore.html', {'data':data,})
