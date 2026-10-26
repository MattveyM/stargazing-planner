// Distance helpers. Real drive times from OpenRouteService come in Week 6;
// for now we estimate drive time from straight-line distance.

const EARTH_RADIUS_MILES = 3958.8;
const toRadians = (degrees) => (degrees * Math.PI) / 180;

// Straight-line ("as the crow flies") distance in miles between two points (haversine formula)
export function distanceMiles(lat1, lon1, lat2, lon2) {
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLon / 2) ** 2;
  return 2 * EARTH_RADIUS_MILES * Math.asin(Math.sqrt(a));
}

// Rough drive-time estimate: roads are about 1.3x longer than a straight line,
// at an average of about 50 mph.
export function estimateDriveMinutes(miles) {
  return Math.round(((miles * 1.3) / 50) * 60);
}

export function formatMinutes(minutes) {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins} min`;
  return mins === 0 ? `${hours} hr` : `${hours} hr ${mins} min`;
}
