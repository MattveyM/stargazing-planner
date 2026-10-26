// All calls to outside services live in this one file.

// Address of our FastAPI back end (set in frontend/.env, with a default for local use)
export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

// GET /api/sites -> list of every dark-sky site from our database
export async function fetchSites() {
  const response = await fetch(`${API_URL}/api/sites`);
  if (!response.ok) throw new Error(`Server error ${response.status}`);
  return response.json();
}

// Turn a typed place name or zip code (like "Bothell" or "98011") into coordinates.
// Uses Open-Meteo's free geocoding service (no API key needed).
async function lookUp(name) {
  const url =
    "https://geocoding-api.open-meteo.com/v1/search?count=1&language=en&format=json&countryCode=US&name=" +
    encodeURIComponent(name);
  const response = await fetch(url);
  if (!response.ok) throw new Error("Location service error");
  const data = await response.json();
  return data.results && data.results.length > 0 ? data.results[0] : null;
}

export async function geocodePlace(placeName) {
  // Try the full text first; if someone typed "Bothell, WA", fall back to just "Bothell".
  let place = await lookUp(placeName);
  if (!place && placeName.includes(",")) {
    place = await lookUp(placeName.split(",")[0].trim());
  }
  if (!place) return null;
  return {
    label: place.admin1 ? `${place.name}, ${place.admin1}` : place.name,
    latitude: place.latitude,
    longitude: place.longitude,
  };
}
