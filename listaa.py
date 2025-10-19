#!/usr/bin/env python3
"""
generate_index.py

Genera una pagina HTML con gli eventi di DaddyLive.
- Gestione sottocategorie tipo "All Soccer Events"
- Filtro SOLO Soccer con ricerca per substring ("soccer" in nome categoria)
- Player in overlay con fullscreen
"""

import requests
import json
import re
from datetime import datetime, timedelta

# ====== CONFIG ======
TIME_OFFSET_HOURS = 2      # +2 ore per l'Italia rispetto all'orario mostrato dal sito
ONLY_SOCCER = True         # True = mostra solo categorie che contengono "soccer"
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

def extract_event_lists(cat_name, events):
    """
    Restituisce una lista di tuple (subcat_name, list_of_events).
    Gestisce sia events come list che come dict (sottocategorie).
    """
    if isinstance(events, list):
        return [(cat_name, events)]
    if isinstance(events, dict):
        out = []
        for sub_name, sub_events in events.items():
            if isinstance(sub_events, list):
                out.append((sub_name, sub_events))
        return out
    return []

url_daddy = "https://dlhd.dad/"
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

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Lista Eventi Daddy</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ font-family: system-ui, Arial, sans-serif; margin: 20px; padding-bottom: 60vh; background: #0f1115; color: #f1f5f9; }}
  input[type="text"] {{ width: 100%; padding: 10px 14px; margin-bottom: 20px; font-size: 16px; border-radius: 10px; border: 1px solid #2a2f3a; background:#131722; color:#e5e7eb; outline: none; }}
  input[type="text"]::placeholder {{ color:#94a3b8; }}

  h1 {{ margin-bottom: 12px; font-weight: 700; }}
  h2 {{ margin-top: 24px; color: #93c5fd; }}
  h3 {{ margin: 12px 0 8px; color: #a5b4fc; }}
  h4 {{ cursor: pointer; margin: 6px 0; padding: 10px 12px; background: #151a28; border: 1px solid #202638; border-radius: 12px; }}

  .event {{ margin-bottom: 12px; padding: 10px; background: #111623; border: 1px solid #1f2435; border-radius: 14px; box-shadow: 0 8px 20px rgba(0,0,0,.35); }}
  .channels {{ margin-left: 8px; margin-top: 8px; display: none; }}

  button {{ margin: 6px 6px 0 0; padding: 10px 14px; font-size: 14px; border: none; border-radius: 10px; cursor: pointer; transition: transform .12s ease, box-shadow .12s ease, background .12s ease; }}
  .btn-play {{ background: linear-gradient(180deg, #22c55e, #16a34a); color: white; box-shadow: 0 2px 10px rgba(34,197,94,.25); }}
  .btn-play:hover {{ transform: translateY(-1px); box-shadow: 0 4px 16px rgba(34,197,94,.35); }}

  /* 🔵 Stile per i pulsanti Karmakurama */
  .btn-karma {{ background: linear-gradient(180deg, #3b82f6, #1d4ed8); color: white; box-shadow: 0 2px 10px rgba(59,130,246,.25); }}
  .btn-karma:hover {{ transform: translateY(-1px); box-shadow: 0 4px 16px rgba(59,130,246,.35); }}

  #playerContainer {{
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80%;
    height: 60%;
    background-color: black;
    z-index: 9999;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,.7);
    display: none;
  }}
  #iframePlayer {{ width: 100%; height: 100%; border: none; }}
  .player-actions {{ position:absolute; top:6px; right:10px; z-index:10001; display:flex; gap:8px; }}
  .ctrl {{ padding: 6px 10px; font-size: 13px; border-radius: 8px; border: 1px solid #2a2f3a; background:#111827; color:#e5e7eb; cursor:pointer; }}
  .time-note {{ font-size:12px; color:#94a3b8; margin: 0 0 10px 2px; }}
</style>
</head>
<body>
<h1>Lista Eventi Daddy (orari mostrati = UK +{TIME_OFFSET_HOURS}h)</h1>
<p class="time-note">Esempio: se sul sito è 19:15, qui vedrai 21:15.</p>
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

function toggleFullscreen() {{
    const iframe = document.getElementById('iframePlayer');
    if (iframe.requestFullscreen) {{ iframe.requestFullscreen(); }}
    else if (iframe.webkitRequestFullscreen) {{ iframe.webkitRequestFullscreen(); }}
    else if (iframe.mozRequestFullScreen) {{ iframe.mozRequestFullScreen(); }}
    else if (iframe.msRequestFullscreen) {{ iframe.msRequestFullscreen(); }}
}}

function togglePlayer() {{
    const container = document.getElementById('playerContainer');
    if (container.style.display === 'none') {{ container.style.display = 'block'; }}
    else {{ container.style.display = 'none'; document.getElementById('iframePlayer').src = ""; }}
}}

function toggleChannels(id) {{
    const elem = document.getElementById(id);
    if (elem.style.display === 'none' || !elem.style.display) {{ elem.style.display = 'block'; }}
    else {{ elem.style.display = 'none'; }}
}}
</script>
"""

# ====== GENERAZIONE EVENTI ======
for day, categories in data_daddy.items():
    html += f"<h2>{day}</h2>\n"
    for category_name, events in categories.items():
        pairs = extract_event_lists(category_name, events)

        for subcat_name, event_list in pairs:
            combined_name = f"{category_name} {subcat_name}".lower()
            if ONLY_SOCCER and 'soccer' not in combined_name:
                continue

            html += f"<h3>{category_name} — {subcat_name}</h3>\n"
            for idx_event, event in enumerate(event_list, start=1):
                event_name = event.get("event", "Senza nome")
                event_time = event.get("time", "").strip()
                if not event_time:
                    continue

                adj_time = adjust_time(event_time, TIME_OFFSET_HOURS)

                all_channels = []
                if "channels" in event and isinstance(event["channels"], list):
                    all_channels.extend(event["channels"])
                if "channels2" in event and isinstance(event["channels2"], list):
                    all_channels.extend(event["channels2"])
                if not all_channels:
                    continue

                event_id = make_id(f"{day}_{category_name}_{subcat_name}_{idx_event}")
                html += f'<div class="event">'
                html += f'<h4 onclick="toggleChannels(\'{event_id}\')">🕒 {adj_time} — {event_name}</h4>\n'
                html += f'<div class="channels" id="{event_id}">\n'

                for idx_ch, ch in enumerate(all_channels, start=1):
                    ch_name, ch_id = "Senza nome", ""
                    if isinstance(ch, dict):
                        ch_name = ch.get("channel_name", "Senza nome")
                        ch_id = str(ch.get("channel_id", "")).strip()
                    elif isinstance(ch, str):
                        ch_name = ch
                        m = re.search(r'\d+', ch)
                        ch_id = m.group(0) if m else ""
                    else:
                        continue

                    if not ch_id:
                        continue

                    # ✅ Link Daddy
                    stream_url_daddy = f"https://dlhd.dad/embed/stream-{ch_id}.php"
                    # ✅ Link Karmakurama
                    stream_url_karma = f"https://ava.karmakurama.com/?id={ch_id}"

                    safe_text = f"{ch_name} [{idx_ch}]".replace('"', '&quot;').replace("'", "\\'")

                    # Pulsante Daddy (verde)
                    html += f'<button class="btn-play" onclick="playInIframe(\'{stream_url_daddy}\')">📺 {safe_text} (Daddy)</button>\n'
                    # Pulsante Karma (blu)
                    html += f'<button class="btn-karma" onclick="playInIframe(\'{stream_url_karma}\')">🔥 {safe_text} (Karma)</button>\n'

                html += '</div></div>\n'

# ====== PLAYER OVERLAY ======
html += """
<div id="playerContainer">
  <div class="player-actions">
    <button class="ctrl" onclick="toggleFullscreen()">🔳 Fullscreen</button>
    <button class="ctrl" onclick="togglePlayer()">✖ Chiudi</button>
  </div>
  <iframe id="iframePlayer" src="" allowfullscreen></iframe>
</div>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ File '{OUTPUT_FILE}' creato con successo!")
