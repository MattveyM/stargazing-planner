// Drive times now come from the server (OpenRouteService), so the browser only needs to format them.

// 95 -> "1 hr 35 min"
export function formatMinutes(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins} min`;
  return mins === 0 ? `${hours} hr` : `${hours} hr ${mins} min`;
}

// Real drive times are shown as-is; estimates get a "~" in front so users know they're rough.
export function formatDrive(site) {
  return `${site.drive_estimated ? "~" : ""}${formatMinutes(site.drive_minutes)}`;
}
