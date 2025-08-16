import requests
import datetime
import json

URL = "https://thedaddy.dad/schedule/schedule-generated.php"
OUTPUT_HTML = "index.html"

def get_today_key():
    today = datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # UTC+2 per l'Italia (gestisce CET/CEST)
    return today.strftime("%A %dth %b %Y - Schedule Time UK GMT")

def main():
    print(f"Scarico JSON Daddy da: {URL}")
    resp = requests.get(URL)
    data = resp.json()

    today_key = get_today_key()
    print(f"Oggi cerco la chiave: {today_key}")

    if today_key not in data:
        print("⚠ Nessuna chiave trovata per oggi!")
        return

    events = data[today_key]

    # HTML base
    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Lista Eventi Daddy - Solo Giorno Odierno</title>
        <style>
            body { font-family: Arial, sans-serif; background: #121212; color: #eee; text-align: center; }
            h1 { color: #ffcc00; }
            input { width: 50%; padding: 8px; margin: 10px; border-radius: 8px; border: none; }
            .event { margin: 8px; padding: 10px; background: #1e1e1e; border-radius: 10px; cursor: pointer; }
            iframe { width: 90%; height: 500px; margin-top: 20px; border: none; }
        </style>
        <script>
            function searchEvents() {
                let input = document.getElementById('search').value.toLowerCase();
                let events = document.getElementsByClassName('event');
                for (let e of events) {
                    e.style.display = e.textContent.toLowerCase().includes(input) ? '' : 'none';
                }
            }
            function playStream(link) {
                document.getElementById('player').src = link;
                window.scrollTo({ top: document.getElementById('player').offsetTop, behavior: 'smooth' });
            }
        </script>
    </head>
    <body>
        <h1>Lista Eventi Daddy - Solo Giorno Odierno</h1>
        <input type="text" id="search" onkeyup="searchEvents()" placeholder="Cerca evento...">
    """

    for ev in events:
        if isinstance(ev, dict):
            ch_name = ev.get("channel_name", "Senza nome")
            stream_id = ev.get("stream_id")
            if stream_id:
                embed_url = f"https://thedaddy.dad/embed/stream-{stream_id}.php"
                html += f'<div class="event" onclick="playStream(\'{embed_url}\')">{ch_name}</div>'

    html += """
        <iframe id="player" allowfullscreen></iframe>
    </body>
    </html>
    """

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ File HTML generato: {OUTPUT_HTML}")

if __name__ == "__main__":
    main()
    # Salvataggio su file HTML
with open("listaa.html", "w", encoding="utf-8") as f:
    f.write(html)
