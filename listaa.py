import requests
import json

# URL della lista JSON
url = "https://thedaddy.dad/schedule/schedule-generated.php"

print(f"Scarico JSON da: {url}")
response = requests.get(url)
if response.status_code != 200:
    print(f"Errore: risposta HTTP {response.status_code}")
    exit(1)

json_text = response.text

try:
    data = json.loads(json_text)
except json.JSONDecodeError as e:
    print(f"Errore parsing JSON: {e}")
    exit(1)

# HTML iniziale con CSS, search, JS e stile player
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Unica Wiseplay</title>
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
div { margin-bottom: 10px; }

#playerContainer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 35vh;
  background-color: black;
  z-index: 9999;
}

#iframePlayer {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
</head>
<body>
<h1>Lista Unica Wiseplay</h1>
<input type="text" id="searchInput" placeholder="Cerca canale/evento...">

<!-- INIZIO iframe calendario daddy live -->
<iframe src="https://watchit.my/iframe.php?u=L3NjaGVkdWxlLnBocA" width="100%" height="2000px" allowfullscreen loading="lazy" title="Match Schedule" style="border:none;"></iframe>
<!-- FINE iframe calendario daddy live -->

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
  if (iframe.requestFullscreen) {
    iframe.requestFullscreen();
  } else if (iframe.webkitRequestFullscreen) {
    iframe.webkitRequestFullscreen();
  } else if (iframe.mozRequestFullScreen) {
    iframe.mozRequestFullScreen();
  } else if (iframe.msRequestFullscreen) {
    iframe.msRequestFullscreen();
  }
}

function togglePlayer() {
  const container = document.getElementById('playerContainer');
  if (container.style.display === 'none') {
    container.style.display = 'block';
  } else {
    container.style.display = 'none';
  }
}
</script>
"""

# Funzione per processare gruppi e canali
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

process_groups(data.get("groups", []))

# Aggiunta iframe player fisso in fondo alla pagina con pulsanti fullscreen e chiusura
html += """
<div id="playerContainer" style="position: fixed; bottom: 0; left: 0; width: 100%; height: 35vh; background-color: black; z-index: 9999;">
  <button onclick="toggleFullscreen()" style="position:absolute; top:5px; right:40px; z-index:10001; padding:6px 10px; font-size:16px;">🔳 Fullscreen</button>
  <button id="closePlayerBtn" onclick="togglePlayer()" style="position:absolute; top:5px; right:10px; z-index:10001; padding:6px 10px; font-size:16px;">X</button>
  <iframe id="iframePlayer" src="" allowfullscreen style="width: 100%; height: 100%; border:none;"></iframe>
</div>

</body>
</html>
"""

# Scrive il file HTML
with open("listaa.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'listaa.html' creato con successo!")
