import requests
import json

# URL lista eventi Daddy
url_daddy = "https://thedaddy.dad/schedule/schedule-generated.php"

# Headers per simulare un browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://thedaddy.dad/"
}

print(f"Scarico JSON Daddy da: {url_daddy}")
response = requests.get(url_daddy, headers=headers)
if response.status_code != 200:
    print(f"Errore: risposta HTTP {response.status_code}")
    exit(1)

try:
    data_daddy = response.json()
except json.JSONDecodeError as e:
    print(f"Errore parsing JSON Daddy: {e}")
    exit(1)

# HTML iniziale combinato
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi e Wiseplay</title>
<style>
body { font-family: sans-serif; margin: 20px; padding-bottom: 60vh; }
input[type="text"] { width: 100%; padding: 10px; margin-bottom: 20px; font-size: 16px; }
button {
  margin: 3px;
  padding: 6px 10px;
  font-size: 14px;
  display: inline-block;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.btn-original { background-color: #4CAF50; color: white; }
.btn-embed    { background-color: #2196F3; color: white; }
.btn-other    { background-color: #f44336; color: white; }
h1 { margin-bottom: 20px; }
h2 { margin-top: 30px; color: #333; }
h3 { margin-top: 15px; color: #666; }
div { margin-bottom: 10px; }
#playerContainer {
  position: fixed; bottom: 0; left: 0; width: 100%; height: 35vh;
  background-color: black; z-index: 9999;
}
#iframePlayer {
  width: 100%; height: 100%; border: none;
}
</style>
</head>
<body>
<h1>Lista Eventi e Wiseplay</h1>
<input type="text" id="searchInput" placeholder="Cerca evento o canale...">

<script>
document.addEventListener("DOMContentLoaded", function() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', function() {
    const filter = searchInput.value.toLowerCase();
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
      const text = button.textContent.toLowerCase();
      button.parentElement.style.display = text.includes(filter) ? '' : 'none';
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
</script>
"""

# ========================
# Sezione 1: Lista Eventi Daddy
# ========================
html += "<h2>Eventi Daddy</h2>\n"
for day, categories in data_daddy.items():
    html += f"<h2>{day}</h2>\n"
    for category_name, events in categories.items():
        html += f"<h3>{category_name}</h3>\n"
        for event in events:
            event_name = event.get("event", "Senza nome")
            event_time = event.get("time", "")
            all_channels = []
            if "channels" in event:
                all_channels.extend(event["channels"])
            if "channels2" in event:
                all_channels.extend(event["channels2"])
            for idx, ch in enumerate(all_channels, start=1):
                ch_name = ch.get("channel_name", "Senza nome")
                ch_id = ch.get("channel_id", "")
                stream_url = f"https://thedaddy.dad/embed/{ch_id}"
                html += f'<div><button class="btn-original" onclick="playInIframe(\'{stream_url}\')">{event_time} - {event_name} ({ch_name}) [{idx}]</button></div>\n'

# ========================
# Sezione 2: Lista Wiseplay (gruppi e stazioni)
# ========================
# URL lista Wiseplay
url_wise = "https://test34344.herokuapp.com/wise/testWise.php?numList=195&tkn=wise"
print(f"Scarico JSON Wise da: {url_wise}")
response = requests.get(url_wise)
if response.status_code != 200:
    print(f"Errore: risposta HTTP {response.status_code}")
    exit(1)

try:
    data_wise = response.json()
except json.JSONDecodeError as e:
    print(f"Errore parsing JSON Wise: {e}")
    exit(1)

def process_groups(groups):
    global html
    for group in groups:
        group_name = group.get("name", "Senza Nome")
        html += f'<h2>{group_name}</h2>\n'
        if "stations" in group:
            for s in group["stations"]:
                name = s.get("name", "Senza Nome").replace('"', "'")
                url = s.get("url", "#")
                if "thedaddy.click/cast/" in url:
                    embed_url = url.replace("thedaddy.click/cast/", "thedaddy.click/embed/")
                    html += f'<div>\n'
                    html += f'<button class="btn-original" onclick="playInIframe(\'{url}\')">{name} (Originale)</button>\n'
                    html += f'<button class="btn-embed" onclick="playInIframe(\'{embed_url}\')">{name} (Embed)</button>\n'
                    html += f'</div>\n'
                else:
                    html += f'<div>\n'
                    html += f'<button class="btn-other" onclick="playInIframe(\'{url}\')">{name}</button>\n'
                    html += f'</div>\n'
        if "groups" in group:
            process_groups(group["groups"])

process_groups(data_wise.get("groups", []))

# ========================
# Player fisso in basso
# ========================
html += """
<div id="playerContainer">
  <button onclick="toggleFullscreen()" style="position:absolute; top:5px; right:40px; z-index:10001;">🔳 Fullscreen</button>
  <button onclick="togglePlayer()" style="position:absolute; top:5px; right:10px; z-index:10001;">X</button>
  <iframe id="iframePlayer" src="" allowfullscreen></iframe>
</div>
</body>
</html>
"""

# Salvataggio HTML
with open("listaa.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'listaa.html' creato con successo!")
