NOVA_WIDGETS.spotify = {
  label: "Spotify",
  sizes: [
    { name: "Klein", w: 2, h: 1 },
    { name: "Mittel", w: 3, h: 2 }
  ],
  defaultSettings: {},
  fields: [],

  render(card) {
    const cover = document.createElement("img");
    cover.style.width = "3rem";
    cover.style.height = "3rem";
    cover.style.borderRadius = "8px";
    cover.style.objectFit = "cover";
    cover.style.display = "none";

    const track = document.createElement("div");
    track.style.fontWeight = "600";
    track.style.marginTop = "4px";
    track.style.textAlign = "center";

    const artist = document.createElement("div");
    artist.style.fontSize = "0.8rem";
    artist.style.opacity = "0.7";

    card.appendChild(cover);
    card.appendChild(track);
    card.appendChild(artist);

    function update() {
      fetch("/api/spotify/now-playing")
        .then(response => response.json())
        .then(data => {
          if (!data.connected) {
            track.textContent = "Nicht verbunden";
            artist.textContent = "";
            cover.style.display = "none";
            return;
          }

          if (!data.playing) {
            track.textContent = "Gerade nichts an";
            artist.textContent = "";
            cover.style.display = "none";
            return;
          }

          track.textContent = data.track;
          artist.textContent = data.artist;
          if (data.image) {
            cover.src = data.image;
            cover.style.display = "block";
          }
        })
        .catch(() => {
          track.textContent = "Spotify nicht erreichbar";
        });
    }

    update();
    const intervalId = setInterval(update, 10000);
    return () => clearInterval(intervalId);
  }
};