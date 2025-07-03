import requests
import json

# URL pubblica della tua lista JSON
url = "https://test34344.herokuapp.com/wise/testWise.php?numList=195&tkn=wise"

# Scarica la pagina
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

# Crea HTML
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi Wiseplay</title>
<style>
body { font-family: sans-serif; margin: 20px; }
input[type="text"] { width: 100%%; padding: 10px; margin-bottom: 20px; font-size: 16px; }

button {
  margin: 3px;
  padding: 6px 10px;
  font-size: 14px;
  display: inline-block;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-original { background-color: #4CAF50; color: white; }    /* verde */
.btn-embed    { background-color: #2196F3; color: white; }    /* blu */
.btn-other    { background-color: #f44336; color: white; }    /* rosso */

h1 { margin-bottom: 20px; }
h2 { margin-top: 30px; color: #333; }
div { margin-bottom: 10px; }
</style>
</head>
<body>
<h1>Eventi Wiseplay (Lista Generata)</h1>

<input type="text" id="searchInput" placeholder="Cerca canale/evento...">

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
</script>
"""

# Funzione ricorsiva per estrarre gruppi e canali, generando HTML direttamente
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
                    html += f'<button class="btn-original" onclick="window.open(\'{url}\', \'_blank\')">{name} (Originale)</button>\n'
                    html += f'<button class="btn-embed" onclick="window.open(\'{embed_url}\', \'_blank\')">{name} (Embed)</button>\n'
                    html += f'</div>\n'
                else:
                    html += f'<div>\n'
                    html += f'<button class="btn-other" onclick="window.open(\'{url}\', \'_blank\')">{name}</button>\n'
                    html += f'</div>\n'
        if "groups" in group:
            process_groups(group["groups"])

process_groups(data.get("groups", []))

html += "</body></html>"

# Scrivi su file
with open("lista.html", "w", encoding="utf-8") as f:
    f.write(html)

print("File 'lista.html' creato con successo!")
