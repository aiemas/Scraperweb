import requests
import datetime
import os

URL = "https://thedaddy.dad/schedule/schedule-generated.php"
OUTPUT_FILE = "listaa.html"

def fetch_data():
    print(f"📥 Scarico JSON Daddy da: {URL}")
    try:
        resp = requests.get(URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Errore durante la richiesta: {e}")
        return None

    try:
        return resp.json()
    except ValueError:
        print("❌ Errore: la risposta non è un JSON valido.")
        print("📄 Contenuto ricevuto:", resp.text[:200], "...")
        return None

def generate_html(data):
    html = """
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Lista Daddy</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #121212 url('https://i.imgur.com/1h9Y5iG.jpg') no-repeat center center fixed;
      background-size: cover;
      color: #fff;
      margin: 0;
      padding: 20px;
    }
    h1 {
      text-align: center;
      color: #ffcc00;
    }
    .channel {
      background: rgba(0, 0, 0, 0.7);
      padding: 10px;
      margin: 10px;
      border-radius: 8px;
    }
    a {
      color: #00ccff;
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
    }
  </style>
</head>
<body>
  <h1>📺 Lista Daddy - Aggiornata {date}</h1>
""".format(date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

    if isinstance(data, list):
        for ch in data:
            if isinstance(ch, dict):
                ch_name = ch.get("channel_name", "Senza nome")
                ch_url = ch.get("url", "#")
                html += f'<div class="channel"><a href="{ch_url}" target="_blank">{ch_name}</a></div>\n'
    else:
        html += "<p>⚠ Nessun dato valido trovato.</p>"

    html += """
</body>
</html>
"""
    return html

def main():
    data = fetch_data()
    if not data:
        print("❌ Nessun dato da salvare, esco.")
        return
    
    html_content = generate_html(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ File HTML generato: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
