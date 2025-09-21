#!/usr/bin/env python3
"""
generate_index.py

Genera una pagina HTML con gli eventi di DaddyLive.
- Gestione sottocategorie tipo "All Soccer Events"
- Filtro SOLO Soccer con ricerca per substring ("soccer" in nome categoria)
- Player Daddy e Karmakurama in iframe (no sandbox, fullscreen abilitato)
"""

import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://dlhd.dad/events.json"

def main():
    resp = requests.get(URL, verify=False)
    resp.raise_for_status()
    data = resp.json()

    soccer_categories = [
        cat for cat in data.get("categories", [])
        if "soccer" in cat.get("name", "").lower()
    ]

    html = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<title>DaddyLive Soccer Events</title>
<style>
body { font-family: Arial, sans-serif; background: #111; color: #eee; padding: 20px; }
h2 { margin-top: 30px; color: #f0f0f0; }
.player-box { margin: 15px 0; padding: 10px; background: #222; border-radius: 10px; }
iframe { width: 100%; height: 400px; border: 0; border-radius: 10px; }
label { display: block; margin-bottom: 6px; font-weight: bold; color: #ddd; }
</style>
</head>
<body>
<h1>⚽ DaddyLive Soccer Events</h1>
"""

    for cat in soccer_categories:
        cat_name = cat.get("name", "Unknown")
        html += f"<h2>{cat_name}</h2>\n"

        all_channels = []
        for sub in cat.get("subcategories", []):
            all_channels.extend(sub.get("channels", []))

        for idx_ch, ch in enumerate(all_channels, start=1):
            ch_id = ch.get("id")
            ch_name = ch.get("name", f"Channel {ch_id}")

            # Link Daddy
            stream_url_daddy = f"https://dlhd.dad/embed/stream-{ch_id}.php"
            # Link Karmakurama
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

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ File index.html generato con successo.")

if __name__ == "__main__":
    main()
