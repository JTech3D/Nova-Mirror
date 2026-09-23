NOVA_WIDGETS.clock = {
  label: "Uhr",
  sizes: [
    { name: "Klein", w: 2, h:2 },
    { name: "Mittel", w: 3, h: 2}
  ],
  defaultSettings: {},
  fields: [],

  render(card) {
    const time = document.createElement("div");
    time.className = "clock-time";
    const date = document.createElement("div");
    date.className = "clock-date";
    card.appendChild(time);
    card.appendChild(date);

    function update() {
      const now = new Date();
      time.textContent = now.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
      date.textContent = now.toLocaleDateString("de-DE", { weekday: "long", day: "numeric", month: "long" });
    }

    update();
    const intervalId = setInterval(update, 1000);
    return () => clearInteraval(intervalId)
  }
};