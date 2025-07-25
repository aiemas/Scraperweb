<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>ScraperWeb Lista Unica</title>
  <style>
    body {
      font-family: sans-serif;
      padding-bottom: 250px; /* spazio per il player */
    }
    .channel-button {
      display: inline-block;
      margin: 3px;
      padding: 6px 12px;
      border-radius: 5px;
      background-color: #2196f3;
      color: white;
      cursor: pointer;
    }
    .player-container {
      position: fixed;
      bottom: 10px;
      left: 50%;
      transform: translateX(-50%);
      width: 90%;
      max-width: 640px;
      background-color: black;
      border: 2px solid #444;
      border-radius: 10px;
      z-index: 9999;
      display: none;
      flex-direction: column;
      align-items: stretch;
    }
    .player-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 5px 10px;
      background-color: #222;
      color: white;
      font-size: 14px;
    }
    .player-iframe {
      width: 100%;
      height: 300px;
      border: none;
      border-bottom-left-radius: 10px;
      border-bottom-right-radius: 10px;
    }
    .fullscreen-button {
      background-color: #444;
      color: white;
      border: none;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>
</head>
<body>

<h1>Lista Unica Canali</h1>

<!-- Esempio pulsanti -->
<div>
  <div class="channel-button" onclick="openPlayer('https://esempio.com/stream1')">Canale 1</div>
  <div class="channel-button" onclick="openPlayer('https://esempio.com/stream2')">Canale 2</div>
  <!-- Aggiungi altri pulsanti dinamicamente dal tuo script Python -->
</div>

<!-- Player fissa -->
<div id="playerBox" class="player-container">
  <div class="player-header">
    <span>In riproduzione</span>
    <button class="fullscreen-button" onclick="toggleFullscreen()">Fullscreen</button>
  </div>
  <iframe id="playerFrame" class="player-iframe" allowfullscreen></iframe>
</div>

<script>
  function openPlayer(url) {
    const playerBox = document.getElementById('playerBox');
    const playerFrame = document.getElementById('playerFrame');
    playerFrame.src = url;
    playerBox.style.display = 'flex';
  }

  function toggleFullscreen() {
    const iframe = document.getElementById('playerFrame');
    if (iframe.requestFullscreen) {
      iframe.requestFullscreen();
    } else if (iframe.webkitRequestFullscreen) {
      iframe.webkitRequestFullscreen();
    } else if (iframe.msRequestFullscreen) {
      iframe.msRequestFullscreen();
    }
  }
</script>

</body>
</html>
