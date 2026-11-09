// Show times in Pacific time no matter where the viewer's computer is set.
const TIME_ZONE = "America/Los_Angeles";

export function formatTime(isoText) {
  return new Date(isoText).toLocaleTimeString("en-US", { timeZone: TIME_ZONE, hour: "numeric", minute: "2-digit" });
}

export function formatHour(isoText) {
  return new Date(isoText).toLocaleTimeString("en-US", { timeZone: TIME_ZONE, hour: "numeric" });
}

// "2026-11-03" -> "Tue, Nov 3". (Noon avoids the date shifting across time zones.)
export function formatNight(dateText, options = { weekday: "short", month: "short", day: "numeric" }) {
  return new Date(`${dateText}T12:00:00`).toLocaleDateString("en-US", options);
}
