import { useEffect, useState } from "react";
import { fetchSites, geocodePlace } from "../api";
import { distanceMiles, estimateDriveMinutes, formatMinutes } from "../utils/distance";
import MapView from "./MapView";
import SiteList from "./SiteList";
import "./SearchPage.css";

export default function SearchPage() {
  // What the user typed / chose
  const [locationText, setLocationText] = useState("");
  const [startPoint, setStartPoint] = useState(null); // { label, latitude, longitude }
  const [maxDriveMinutes, setMaxDriveMinutes] = useState(120);

  // Data from the back end
  const [allSites, setAllSites] = useState([]);
  const [results, setResults] = useState(null); // null = no search yet
  const [searchedFrom, setSearchedFrom] = useState(null); // the point the current results are for

  // Messages for the user
  const [status, setStatus] = useState("Connecting to the server...");
  const [error, setError] = useState("");

  // When the page first loads, get all sites from our FastAPI back end.
  useEffect(() => {
    fetchSites()
      .then((sites) => {
        setAllSites(sites);
        setStatus(`Connected: ${sites.length} dark-sky sites in the database.`);
      })
      .catch(() => {
        setStatus("");
        setError("Can't reach the server. Is the FastAPI back end running?");
      });
  }, []);

  // "Use my location" button: ask the browser for GPS coordinates.
  function handleUseMyLocation() {
    setError("");
    if (!navigator.geolocation) {
      setError("Your browser doesn't support location.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const point = {
          label: "My location",
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        setStartPoint(point);
        setLocationText(`My location (${point.latitude.toFixed(3)}, ${point.longitude.toFixed(3)})`);
      },
      () => setError("Location permission was denied. Type a city instead."),
    );
  }

  // "Find stargazing spots" button
  async function handleSearch(event) {
    event.preventDefault(); // stop the form from reloading the page
    setError("");

    let point = startPoint;
    if (!point) {
      if (!locationText.trim()) {
        setError("Enter a city or use your location first.");
        return;
      }
      try {
        point = await geocodePlace(locationText.trim());
      } catch {
        setError("Couldn't reach the location lookup service. Check your internet connection.");
        return;
      }
      if (!point) {
        setError(`Couldn't find "${locationText}". Try a city name like "Bothell" or a zip code.`);
        return;
      }
      setStartPoint(point);
    }

    // Add distance + estimated drive time to every site, keep the ones within range, closest first.
    const nearby = allSites
      .map((site) => {
        const miles = distanceMiles(point.latitude, point.longitude, site.latitude, site.longitude);
        return { ...site, miles, driveMinutes: estimateDriveMinutes(miles) };
      })
      .filter((site) => site.driveMinutes <= maxDriveMinutes)
      .sort((a, b) => a.driveMinutes - b.driveMinutes);

    setResults(nearby);
    setSearchedFrom(point);
    setStatus(`${nearby.length} sites within about ${formatMinutes(maxDriveMinutes)} of ${point.label}.`);
  }

  return (
    <main className="search-page">
      <h1>Find the best night and place to stargaze</h1>
      <p className="subtitle">See the darkest spots near you in the Pacific Northwest.</p>

      <form className="search-card" onSubmit={handleSearch}>
        <label htmlFor="location">Starting location</label>
        <div className="location-row">
          <input
            id="location"
            type="text"
            placeholder="City or zip code (e.g., Bothell)"
            value={locationText}
            onChange={(e) => {
              setLocationText(e.target.value);
              setStartPoint(null); // typing a new place clears the old coordinates
            }}
          />
          <button type="button" className="secondary" onClick={handleUseMyLocation}>
            Use my location
          </button>
        </div>

        <label htmlFor="drive">
          Max drive time: <strong>{formatMinutes(maxDriveMinutes)}</strong>
        </label>
        <input
          id="drive"
          type="range"
          min="30"
          max="300"
          step="15"
          value={maxDriveMinutes}
          onChange={(e) => setMaxDriveMinutes(Number(e.target.value))}
        />
        <div className="range-labels">
          <span>30 min</span>
          <span>5 hr</span>
        </div>

        <button type="submit" className="primary">
          Find stargazing spots
        </button>
      </form>

      {error && <p className="error">{error}</p>}
      {status && <p className="status">{status}</p>}

      {/* Before a search the map shows every site; after a search it shows only the results. */}
      <MapView sites={results ?? allSites} startPoint={searchedFrom} />

      {results && (
        <section>
          <h2>Results</h2>
          <p className="note">
            Drive times are estimates from straight-line distance. Real drive times and nightly scores come next.
          </p>
          <SiteList sites={results} />
        </section>
      )}
    </main>
  );
}
