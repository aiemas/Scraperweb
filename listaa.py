import requests
import json
import re
from datetime import datetime, timedelta

# ====== CONFIG ======
TIME_OFFSET_HOURS = 2      # +2 ore per l'Italia rispetto all'orario mostrato dal sito
ONLY_SOCCER = True         # True = mostra solo categoria "Soccer", False = tutte
OUTPUT_FILE = "listaa.html"
# =====================

# Funzione per creare ID validi da stringhe
def make_id(s):
    return re.sub(r'\W+', '_', s)

# Funzione per filtrare solo il giorno odierno (in base all’intestazione tipo "Friday 15th Aug 2025 - ...")
def is_today(day_string):
    try:
        date_part = day_string.split("-")[0].strip()  # es: "Friday 15th Aug 2025"
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

# Somma ore a una stringa HH:MM; ritorna "HH:MM" e aggiunge "(+1)" se passa a giorno successivo
def adjust_time(time_str, offset_hours=2):
    try:
        t = datetime.strptime(time_str.strip(), "%H:%M")
        t2 = t + timedelta(hours=offset_hours)
        rolled = (t2.day != t.day)  # se supera mezzanotte
        out = t2.strftime("%H:%M")
        return out + (" (+1)" if rolled else "")
    except:
        return time_str  # se non parsabile, mostra quello originale

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

# HTML iniziale (con stile un po' più carino)
html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi Daddy</title>
<style>
  :root { color-scheme: dark; }
  body { font-family: system-ui, Arial, sans-serif; margin: 20px; padding-bottom: 60vh; background: #0f1115; color: #f1f5f9; }
  input[type="text"] { width: 100%; padding: 10px 14px; margin-bottom: 20px; font-size: 16px; border-radius: 10px; border: 1px solid #2a2f3a; background:#131722; color:#e5e7eb; outline: none; }
  input[type="text"]::placeholder { color:#94a3b8; }

  h1 { margin-bottom: 12px; font-weight: 700; }
  h2 { margin-top: 24px; color: #93c5fd; }
  h3 { margin: 12px 0 8px; color: #a5b4fc; }
  h4 { cursor: pointer; margin: 6px 0; padding: 10px 12px; background: #151a28; border: 1px solid #202638; border-radius: 12px; }

  .event { margin-bottom: 12px; padding: 10px; background: #111623; border: 1px solid #1f2435; border-radius: 14px; box-shadow: 0 8px 20px rgba(0,0,0,.35); }
  .channels { margin-left: 8px; margin-top: 8px; display: none; }

  button { margin: 6px 6px 0 0; padding: 10px 14px; font-size: 14px; border: none; border-radius: 10px; cursor: pointer; transition: transform .12s ease, box-shadow .12s ease, background .12s ease; }
  .btn-play { background: linear-gradient(180deg, #22c55e, #16a34a); color: white; box-shadow: 0 2px 10px rgba(34,197,94,.25); }
  .btn-play:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(34,197,94,.35); }

  #playerContainer { position: fixed; bottom: 0; left: 0; width: 100%; height: 35vh; background-color: black; z-index: 9999; border-top: 1px solid #222; }
  #iframePlayer { width: 100%; height: 100%; border: none; }
  .player-actions { position:absolute; top:6px; right:10px; z-index:10001; display:flex; gap:8px; }
  .ctrl { padding: 6px 10px; font-size: 13px; border-radius: 8px; border: 1px solid #2a2f3a; background:#111827; color:#e5e7eb; cursor:pointer; }
  .time-note { font-size:12px; color:#94a3b8; margin: 0 0 10px 2px; }
</style>
</head>
<body>
<h1>Lista Eventi Daddy (orari mostrati = UK +{offset}h)</h1>
<p class="time-note">Esempio: se sul sito è 19:15, qui vedrai 21:15.</p>
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
    if (elem.style.display === 'none' || !elem.style.display) { elem.style.display = 'block';
    } else { elem.style.display = 'none'; }
}
</script>
""".replace("{offset}", str(TIME_OFFSET_HOURS))

# Generazione eventi (solo oggi; opzionale filtro Soccer)
for day, categories in data_daddy.items():
    if not is_today(day):
        continue
    html += f"<h2>{day}</h2>\n"
    for category_name, events in categories.items():
        if ONLY_SOCCER and category_name.lower() != "soccer":
            continue
        html += f"<h3>{category_name}</h3>\n"
        for idx_event, event in enumerate(events, start=1):
            event_name = event.get("event", "Senza nome")
            event_time = event.get("time", "").strip()
            if not event_time:
                continue

            # Somma +2 ore all’orario di partenza
            adj_time = adjust_time(event_time, TIME_OFFSET_HOURS)

            # Unisci channels/channels2
            all_channels = []
            if "channels" in event and isinstance(event["channels"], list):
                all_channels.extend(event["channels"])
            if "channels2" in event and isinstance(event["channels2"], list):
                all_channels.extend(event["channels2"])
            if not all_channels:
                continue

            event_id = make_id(f"{day}_{category_name}_{idx_event}")
            html += f'<div class="event">'
            html += f'<h4 onclick="toggleChannels(\'{event_id}\')">🕒 {adj_time} — {event_name}</h4>\n'
            html += f'<div class="channels" id="{event_id}">\n'

            # Bottoni canali (tutti in formato dad/embed/stream-XXX.php come richiesto)
            for idx_ch, ch in enumerate(all_channels, start=1):
                ch_name, ch_id = "Senza nome", ""
                if isinstance(ch, dict):
                    ch_name = ch.get("channel_name", "Senza nome")
                    ch_id = str(ch.get("channel_id", "")).strip()
                elif isinstance(ch, str):
                    ch_name = ch
                    m = re.search(r'\d+', ch)  # estrai un numero se presente
                    ch_id = m.group(0) if m else ""
                else:
                    continue

                if not ch_id:
                    continue  # se non ho un ID numerico non posso creare l'embed

                stream_url = f"https://thedaddy.dad/embed/stream-{ch_id}.php"
                safe_text = f"{ch_name} [{idx_ch}]".replace('"', '&quot;').replace("'", "\\'")
                html += f'<button class="btn-play" onclick="playInIframe(\'{stream_url}\')">📺 {safe_text}</button>\n'

            html += '</div></div>\n'

# Player fisso
html += """
<div id="playerContainer">
  <div class="player-actions">
    <button class="ctrl" onclick="toggleFullscreen()">🔳 Fullscreen</button>
    <button class="ctrl" onclick="togglePlayer()">Chiudi</button>
  </div>
  <iframe id="iframePlayer" src="" allowfullscreen></iframe>
</div>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ File '{OUTPUT_FILE}' creato con successo!")
