import requests
import json
import re
from datetime import datetime

# Funzione per creare ID validi da stringhe
def make_id(s):
    return re.sub(r'\W+', '_', s)

# Funzione per filtrare solo il giorno odierno
def is_today(day_string):
    try:
        date_part = day_string.split("-")[0].strip()
        for suf in ["th","st","nd","rd",","]:
            date_part = date_part.replace(suf,"")
        parts = date_part.strip().split()
        if len(parts) < 3:
            return False
        day_month_year = " ".join(parts[-3:])  # "15 Aug 2025"
        day_dt = datetime.strptime(day_month_year, "%d %b %Y")
        return day_dt.date() == datetime.today().date()
    except:
        return False

# URL lista eventi Daddy
url_daddy = "https://thedaddy.dad/schedule/schedule-generated.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://thedaddy.dad/"
}

print(f"Scarico JSON Daddy da: {url_daddy}")
try:
    response = requests.get(url_daddy, headers=headers, timeout=15)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"❌ Errore richiesta: {e}")
    exit(1)

try:
    data_daddy = response.json()
except json.JSONDecodeError as e:
    print(f"❌ Errore parsing JSON Daddy: {e}")
    print("📄 Contenuto ricevuto:", response.text[:200], "...")
    exit(1)

# HTML iniziale
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi Daddy</title>
<style>
body { font-family: sans-serif; margin: 20px; padding-bottom: 60vh; background: #121212; color: #fff; }
input[type="text"] { width: 100%; padding: 10px; margin-bottom: 20px; font-size: 16px; }

h1, h2, h3, h4 { margin-bottom: 10px; }
h4 { cursor: pointer; }

div.event { margin-bottom: 10px; }
div.channels { margin-left: 20px; display: none; }

button { margin: 3px; padding: 6px 10px; font-size: 14px; border: none; border-radius: 5px; cursor: pointer; }
.btn-original { background-color: #4CAF50; color: white; }

#playerContainer { position: fixed; bottom: 0; left: 0; width: 100%; height: 35vh; background-color: black; z-index: 9999; }
#iframePlayer { width: 100%; height: 100%; border: none; }
</style>
</head>
<body>
<h1>Lista Eventi Daddy - Solo Giorno Odierno</h1>
<input type="text" id="searchInput" placeholder="Cerca evento o canale...">

<script>
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function() {
        const filter = searchInput.value.toLowerCase();
        const events = document.querySelectorAll('div.event');
        events.forEach(eventDiv => {
            const text = eventDiv.textContent.toLowerCase();
            eventDiv.style.display = text.includes(filter) ? '' : 'none';
        });
    });
});

function playInIframe(url) {
    document.getElementById('iframePlayer').src = url;
}

function toggleFullscreen() {
    const iframe = document.getElementById('iframePlayer');
    if (iframe.requestFullscreen) { iframe.requestFullscreen();
    } else if (iframe.webkitRequestFullscreen) { iframe.webkitRequestFullscreen();
    } else if (iframe.mozRequestFullScreen) { iframe.mozRequestFullScreen();
    } else if (iframe.msRequestFullscreen) { iframe.msRequestFullscreen(); }
}

function togglePlayer() {
    const container = document.getElementById('playerContainer');
    if (container.style.display === 'none') { container.style.display = 'block';
    } else { container.style.display = 'none'; }
}

function toggleChannels(id) {
    const elem = document.getElementById(id);
    if (elem.style.display === 'none') { elem.style.display = 'block';
    } else { elem.style.display = 'none'; }
}
</script>
"""

# Generazione eventi solo odierni
for day, categories in data_daddy.items():
    if not is_today(day):
        continue
    html += f"<h2>{day}</h2>\n"
    for category_name, events in categories.items():
        html += f"<h3>{category_name}</h3>\n"
        for idx_event, event in enumerate(events, start=1):
            event_name = event.get("event", "Senza nome")
            event_time = event.get("time", "")
            all_channels = []
            if "channels" in event:
                all_channels.extend(event["channels"])
            if "channels2" in event:
                all_channels.extend(event["channels2"])
            if not all_channels:
                continue
            event_id = make_id(f"{day}_{idx_event}")
            html += f'<div class="event">'
            html += f'<h4 onclick="toggleChannels(\'{event_id}\')">{event_time} - {event_name}</h4>\n'
            html += f'<div class="channels" id="{event_id}">\n'
            for idx_ch, ch in enumerate(all_channels, start=1):
                if isinstance(ch, dict):  # Controlla se 'ch' è un dizionario
                    ch_name = ch.get("channel_name", "Senza nome")
                    ch_id = ch.get("channel_id", "")
                elif isinstance(ch, str):  # Controlla se 'ch' è una stringa
                    ch_name = ch  # Usa il valore della stringa come nome del canale
                    ch_id = make_id(ch_name)  # Se è necessario un ID
                else:
                    continue  # Ignora i casi non desiderati
                stream_url = f"https://thedaddy.dad/embed/stream-{ch_id}"
                html += f'<button class="btn-original" onclick="playInIframe(\'{stream_url}\')">{ch_name} [{idx_ch}]</button>\n'
            html += '</div></div>\n'

# Player fisso
html += """
<div id="playerContainer">
  <button onclick="toggleFullscreen()" style="position:absolute; top:5px; right:40px; z-index:10001;">🔳 Fullscreen</button>
  <button onclick="togglePlayer()" style="position:absolute; top:5px; right:10px; z-index:10001;">X</button>
  <iframe id="iframePlayer" src="" allowfullscreen></iframe>
</div>
</body>
</html>
"""

with open("listaa.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ File 'listaa.html' creato con successo!")
