const WEATHER_CODES = {
    0: ["☀️", "Klar"],
    1: ["🌤️", "Überwiegend klar"],
    2: ["⛅", "Teilweise bewölkt"],
    3: ["☁️", "Bedeckt"],
    45: ["🌫️", "Nebel"],
    61: ["🌧️", "Leichter Regen"],
    63: ["🌧️", "Regen"],
    71: ["🌨️", "Schnee"],
    95: ["⛈️", "Gewitter"]
};

NOVA_WIDGETS.weather = {
    label: "Wetter",
    sizes: [
        { name: "Klein", w: 3, h: 2 },
        { name: "Mittel", w: 4, h: 3 },
        { name: "Groß", w: 5, h: 4}
    ],
    defaultSettings: { name:"", latitude: 0, longitude: 0 },
    fields: [
        { key: "name", label: "Ortsname", type: "text" },
        { key: "latitude", label: "Breitengrad", type: "number" },
        { key: "longitude", label: "Längengrad", type: "number" }
    ],

    render(card, widget) {
        const emoji = document.createElement("div");
        emoji.style.fontSize = "2rem";
        const temp = document.createElement("div");
        temp.className = "weather-temp";
        const desc = document.createElement("div");
        desc.className = "weather-temp";
        const location = document.createElement("div");
        location.className = "weather-location";
        location.textContent = widget.settings.name;

        card.appendChild(emoji);
        card.appendChild(temp);
        card.appendChild(desc);
        card.appendChild(location);
    
        const { latitude, longitude } = widget.settings;
        const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,weather_code`;

        fetch(url)
        .then(response => response.json())
        .then(data => {
            const code = data.current.weather.code;
            const [icon, text] = WEATHER_CODES[code] || ["❓", "Unbekannt"];
            emoji.textContent = icon;
            temp.textContent = Math.round(data.current.temperature_2m) + "°C";
            desc.textContent = text;
        })
        .catch(() => {
            desc.textContent = "Wetterdaten nicht verfügbar";
        });
    }
};