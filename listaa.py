#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

# ====== CONFIG ======
TIME_OFFSET_HOURS = 2
OUTPUT_FILE = "listaa.html"
# =====================

def make_id(s):
    return re.sub(r'\W+', '_', s)

def adjust_time(time_str, offset_hours=2):
    try:
        t = datetime.strptime(time_str.strip(), "%H:%M")
        t2 = t + timedelta(hours=offset_hours)
        rolled = (t2.day != t.day)
        out = t2.strftime("%H:%M")
        return out + (" (+1)" if rolled else "")
    except:
        return time_str

# Scarico pagina Daddy
url = "https://dlhd.dad/index.php?cat=All+Soccer+Events"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
print(f"🌐 Scarico pagina: {url}")
response = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(response.text, "html.parser")

# Estraggo eventi reali (solo nomi con " - ")
events = []
seen = set()
for a in soup.select("a[href*='watch.php?id=']"):
    name = a.get_text(strip=True)
    href = a["href"]
    if not href.startswith("http"):
        href = "https://dlhd.dad/" + href.lstrip("/")

    # estraggo solo id numerico
    m = re.search(r'id=(\d+)', href)
    if not m:
        continue
    ch_id = m.group(1)

    if " - " in name and name not in seen:
        seen.add(name)
        events.append({
            "name": name,
            "id": ch_id
        })

print(f"✅ Trovati {len(events)} eventi")

# ====== GENERAZIONE HTML ======
html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi Daddy</title>
<style>
body {{ font-family: system-ui, Arial; background:#0f1115; color:#f1f5f9; padding:20px; }}
input[type=text] {{ width:100%; padding:10px; margin-bottom:20px; font-size:16px; border-radius:10px; border:1px solid #2a2f3a; background:#131722; color:#e5e7eb; }}
button {{ margin:6px 6px 0 0; padding:10px 14px; border:none; border-radius:10px; cursor:pointer; }}
.btn-play {{ background:linear-gradient(180deg,#22c55e,#16a34a); color:white; }}
.btn-karma {{ background:linear-gradient(180deg,#3b82f6,#1d4ed8); color:white; }}
.event {{ margin-bottom:12px; padding:10px; background:#111623; border-radius:14px; }}
.channels {{ margin-left:8px; margin-top:8px; display:none; }}
#playerContainer {{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); width:80%; height:60%; background:black; z-index:9999; display:none; border-radius:12px; }}
#iframePlayer {{ width:100%; height:100%; border:none; }}
.player-actions {{ position:absolute; top:6px; right:10px; z-index:10001; display:flex; gap:8px; }}
.ctrl {{ padding:6px 10px; font-size:13px; border-radius:8px; border:1px solid #2a2f3a; background:#111827; color:#e5e7eb; cursor:pointer; }}
</style>
</head>
<body>
<h1>Lista Eventi Daddy (orari mostrati = UK +{TIME_OFFSET_HOURS}h)</h1>
<input type="text" id="searchInput" placeholder="Cerca evento o canale...">
<script>
document.addEventListener("DOMContentLoaded", function() {{
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function() {{
        const filter = searchInput.value.toLowerCase();
        const events = document.querySelectorAll('div.event');
        events.forEach(eventDiv => {{
            const text = eventDiv.textContent.toLowerCase();
            eventDiv.style.display = text.includes(filter) ? '' : 'none';
        }});
    }});
}});
function playInIframe(url) {{
    const container = document.getElementById('playerContainer');
    const iframe = document.getElementById('iframePlayer');
    iframe.src = url;
    container.style.display = 'block';
}}
function togglePlayer() {{
    const container = document.getElementById('playerContainer');
    if(container.style.display==='none'){{container.style.display='block';}}
    else{{container.style.display='none';document.getElementById('iframePlayer').src='';}}
}}
function toggleChannels(id) {{
    const elem = document.getElementById(id);
    elem.style.display = (elem.style.display==='none'||!elem.style.display)?'block':'none';
}}
</script>
"""

for idx, e in enumerate(events, start=1):
    event_id = make_id(f"event_{idx}")
    stream_url_daddy = f"https://dlhd.dad/embed/stream-{e['id']}.php"
    stream_url_karma = f"https://ava.karmakurama.com/?id={e['id']}"
    html += f'<div class="event">'
    html += f'<h4 onclick="toggleChannels(\'{event_id}\')">🕒 {e["name"]}</h4>'
    html += f'<div class="channels" id="{event_id}">'
    html += f'<button class="btn-play" onclick="playInIframe(\'{stream_url_daddy}\')">📺 Daddy</button>'
    html += f'<button class="btn-karma" onclick="playInIframe(\'{stream_url_karma}\')">🔥 Karma</button>'
    html += '</div></div>\n'

# Player overlay
html += """
<div id="playerContainer">
  <div class="player-actions">
    <button class="ctrl" onclick="togglePlayer()">✖ Chiudi</button>
  </div>
  <iframe id="iframePlayer" src="" allowfullscreen></iframe>
</div>
</body></html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ File '{OUTPUT_FILE}' creato con successo!")
