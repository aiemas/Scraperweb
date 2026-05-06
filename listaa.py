#!/usr/bin/env python3

import requests
import re
from datetime import datetime, timedelta
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TIME_OFFSET_HOURS = 2
OUTPUT_FILE = "listaa.html"

URL_DADDY = "https://dlstreams.com/index.php?cat=Soccer"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://thedaddy.dad/"
}

def make_id(s):
    return re.sub(r'\W+','_',s)

def adjust_time(time_str,offset=2):
    try:
        t=datetime.strptime(time_str,"%H:%M")
        t2=t+timedelta(hours=offset)
        rolled=(t2.day!=t.day)
        out=t2.strftime("%H:%M")
        return out+(" (+1)" if rolled else "")
    except:
        return time_str


print("Scarico pagina Daddy...")

r=requests.get(URL_DADDY,headers=HEADERS,verify=False)
html_page=r.text

events=[]

blocks=re.findall(
    r'schedule__time.*?data-time="(.*?)".*?schedule__eventTitle">(.*?)<.*?schedule__channels">(.*?)</div>',
    html_page,
    re.S
)

for time_str,title,channels_html in blocks:

    title=re.sub("<.*?>","",title).strip()
    adj_time=adjust_time(time_str,TIME_OFFSET_HOURS)

    channels=re.findall(
        r'href="/watch\.php\?id=(\d+)".*?>(.*?)<',
        channels_html
    )

    ch_list=[]

    for ch_id,ch_name in channels:
        stream_url=f"https://dlstreams.top/embed/stream-{ch_id}.php"
        ch_list.append({
            "name":ch_name.strip(),
            "url":stream_url
        })

    if ch_list:
        events.append({
            "time":adj_time,
            "event":title,
            "channels":ch_list
        })


html=f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi Daddy</title>

<style>

body {{
font-family:Arial;
margin:20px;
background:#0f1115;
color:white;
}}

input {{
width:100%;
padding:10px;
margin-bottom:20px;
border-radius:8px;
border:none;
background:#1a1f2e;
color:white;
}}

h4 {{
cursor:pointer;
padding:10px;
background:#151a28;
border-radius:8px;
}}

.event {{
margin-bottom:12px;
padding:10px;
background:#111623;
border-radius:10px;
}}

.channels {{
display:none;
margin-top:8px;
}}

button {{
margin:6px;
padding:10px 14px;
border:none;
border-radius:8px;
cursor:pointer;
background:#16a34a;
color:white;
}}

#playerContainer {{
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:rgba(0,0,0,0.9);
z-index:9999;
display:none;
justify-content:center;
align-items:center;
flex-direction:column;
}}

#iframePlayer {{
width:90%;
height:80%;
border:none;
border-radius:10px;
}}

.ctrl {{
background:#1f2937;
margin:5px;
padding:8px 12px;
}}

</style>

</head>

<body>

<h1>Eventi Soccer</h1>

<input type="text" id="searchInput" placeholder="Cerca evento...">

<script>

document.addEventListener("DOMContentLoaded",function(){{

var input=document.getElementById("searchInput");

input.addEventListener("input",function(){{

var filter=input.value.toLowerCase();

var events=document.querySelectorAll(".event");

events.forEach(function(e){{

var txt=e.textContent.toLowerCase();

if(txt.includes(filter)){{

e.style.display="";

}}else{{

e.style.display="none";

}}

}});

}});

}});

function playInIframe(url){{

var c=document.getElementById("playerContainer");
var i=document.getElementById("iframePlayer");

i.src="";
setTimeout(function(){{
    i.src=url;
}},100);

c.style.display="flex";

}}

function togglePlayer(){{
var c=document.getElementById("playerContainer");
c.style.display="none";
document.getElementById("iframePlayer").src="";
}}

function toggleFullscreen(){{
var iframe=document.getElementById("iframePlayer");
if(iframe.requestFullscreen){{
    iframe.requestFullscreen();
}}
}}

function toggleChannels(id){{

var e=document.getElementById(id);

if(e.style.display==="none"||!e.style.display){{
    e.style.display="block";
}}else{{
    e.style.display="none";
}}

}}

</script>
"""

for idx,event in enumerate(events,1):

    event_id=make_id(f"ev_{idx}")

    html+=f'<div class="event">'
    html+=f'<h4 onclick="toggleChannels(\'{event_id}\')">🕒 {event["time"]} — {event["event"]}</h4>'
    html+=f'<div class="channels" id="{event_id}">'

    for i,ch in enumerate(event["channels"],1):

        safe=ch["name"].replace('"','&quot;')

        html+=f'<button onclick="playInIframe(\'{ch["url"]}\')">📺 {safe} [{i}]</button>'

    html+='</div></div>'


html+="""

<div id="playerContainer">

<div>
<button class="ctrl" onclick="toggleFullscreen()">Fullscreen</button>
<button class="ctrl" onclick="togglePlayer()">Chiudi</button>
</div>

<iframe id="iframePlayer"></iframe>

</div>

</body>
</html>
"""

with open(OUTPUT_FILE,"w",encoding="utf8") as f:
    f.write(html)

print("HTML creato:",OUTPUT_FILE)
