#!/usr/bin/env python3
"""
generate_index.py

Genera una pagina HTML con gli eventi di DaddyLive.
- Gestione sottocategorie tipo "All Soccer Events"
- Filtro SOLO Soccer con ricerca per substring ("soccer" in nome categoria)
- Player Daddy e Karmakurama in iframe (no sandbox, fullscreen abilitato)
"""

import requests
import json
import re
from datetime import datetime, timedelta

# ====== CONFIG ======
TIME_OFFSET_HOURS = 2      # +2 ore per l'Italia rispetto all'orario mostrato dal sito
ONLY_SOCCER = True         # True = mostra solo categorie che contengono "soccer"
OUTPUT_FILE = "index.html"
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

# ====== RICHIESTA JSON DADDY ======
url_daddy = "https://daddylivestream.com/schedule/schedule-generated.php"
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

# ====== GENERAZIONE HTML ======
html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>DaddyLive Soccer Events</title>
<style>
body {{ font-family: Arial, sans-serif; background: #111; color: #eee; padding: 20px; }}
h2 {{ margin-top: 30px; color: #f0f0f0; }}
.player-box {{ margin: 15px 0; padding: 10px; background: #222; border-radius: 10px; }}
iframe {{ width: 100%; height: 400px; border: 0; border-radius: 10px; }}
label {{ display: block; margin-bottom: 6px; font-weight: bold; color: #ddd; }}
</style>
</head>
<body>
<h1>⚽ DaddyLive Soccer Events (orari mostrati = UK +{TIME_OFFSET_HOURS}h)</h1>
<p>Se sul sito è 19:15, qui vedrai {adjust_time("19:15", TIME_OFFSET_HOURS)}</p>
"""

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

                    html += f"""
<div class="player-box">
  <label>{safe_text} - Daddy</label>
  <iframe src="{stream_url_daddy}" allowfullscreen referrerpolicy="no-referrer"></iframe>
</div>
<div class="player-box">
  <label>{safe_text} - Karmakurama</label>
  <iframe src="{stream_url_karma}" allowfullscreen referrerpolicy="no-referrer"></iframe>
</div>
"""

html += """
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ File '{OUTPUT_FILE}' creato con successo!")
