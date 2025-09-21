#!/usr/bin/env python3
"""
generate_index.py

Genera una pagina HTML con gli eventi di DaddyLive.
- Gestione sottocategorie tipo "All Soccer Events"
- Filtro SOLO Soccer con ricerca per substring ("soccer" in nome categoria)
- Pulsanti Daddy + Karmakurama che aprono in browser esterno
"""

import requests
import json
import re

# URL JSON eventi (modifica se diverso)
URL = "https://dlhd.dad/events.json"

def main():
    resp = requests.get(URL)
    resp.raise_for_status()
    data = resp.json()

    # Filtra solo categorie con "soccer"
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
button { padding: 10px 16px; border: none; border-radius: 8px; margin: 6px; cursor: pointer; font-size: 15px; transition: all .2s; }
.btn-play { background: linear-gradient(180deg, #22c55e, #15803d); color: white; box-shadow: 0 2px 10px rgba(34,197,94,.25); }
.btn-play:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(34,197,94,.35); }
.btn-karma { background: linear-gradient(180deg, #3b82f6, #1d4ed8); color: white; box-shadow: 0 2px 10px rgba(59,130,246,.25); }
.btn-karma:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(59,130,246,.35); }
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

            # ✅ Link Daddy
            stream_url_daddy = f"https://dlhd.dad/embed/stream-{ch_id}.php"
            # ✅ Link Karmakurama
            stream_url_karma = f"https://ava.karmakurama.com/?id={ch_id}"

            safe_text = f"{ch_name} [{idx_ch}]".replace('"', '&quot;').replace("'", "\\'")

            # Pulsante Daddy → apre nel browser esterno
            html += f'<a href="{stream_url_daddy}" target="_blank" rel="noopener noreferrer"><button class="btn-play">📺 {safe_text} (Daddy)</button></a>\n'

            # Pulsante Karma → apre nel browser esterno
            html += f'<a href="{stream_url_karma}" target="_blank" rel="noopener noreferrer"><button class="btn-karma">🔥 {safe_text} (Karma)</button></a>\n'

    html += """
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ File index.html generato con successo.")

if __name__ == "__main__":
    main()
