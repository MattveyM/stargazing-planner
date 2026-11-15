import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import { fetchRankingCalendar, fetchRankings, fetchSites, geocodePlace } from "../api";
import { formatMinutes } from "../utils/distance";
import { formatNight } from "../utils/time";
import MapView from "./MapView";
import NightCalendar from "./NightCalendar";
import SiteList from "./SiteList";
import "./SearchPage.css";

export default function SearchPage() {
  // What the user typed / chose
  const [locationText, setLocationText] = useState("");
  const [startPoint, setStartPoint] = useState(null); // { label, latitude, longitude }
  const [maxDriveMinutes, setMaxDriveMinutes] = useState(120);

  // Data from the back end
  const [allSites, setAllSites] = useState([]);
  const [rankings, setRankings] = useState(null); // null = no search yet; else { night, drive_source, results }
  const [calendar, setCalendar] = useState([]); // best score for each of the next 7 nights
  const [search, setSearch] = useState(null); // { point, maxDrive } the current results are for
  const [selectedId, setSelectedId] = useState(null); // site picked in the list or on the map

  // Messages for the user
  const [loading, setLoading] = useState("");
  const [status, setStatus] = useState("Connecting to the server...");
  const [error, setError] = useState("");

  // When the page first loads, get all sites so the map isn't empty before a search.
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

  // Ask the server to rank sites for one night (null = tonight).
  async function loadRankings(point, maxDrive, night) {
    const data = await fetchRankings({ latitude: point.latitude, longitude: point.longitude, maxDrive, night });
    setRankings(data);
    setSelectedId(null); // nothing selected until the user clicks a row or marker
    const when = night ? formatNight(data.night) : "tonight";
    setStatus(`${data.results.length} sites within ${formatMinutes(maxDrive)} of ${point.label}, ranked for ${when}.`);
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
      setLoading("Looking up that place...");
      try {
        point = await geocodePlace(locationText.trim());
      } catch {
        setLoading("");
        setError("Couldn't reach the location lookup service. Check your internet connection.");
        return;
      }
      if (!point) {
        setLoading("");
        setError(`Couldn't find "${locationText}". Try a city name like "Bothell" or a zip code.`);
        return;
      }
      setStartPoint(point);
    }

    setLoading("Finding the best spots and drive times...");
    try {
      const where = { latitude: point.latitude, longitude: point.longitude, maxDrive: maxDriveMinutes };
      const [, nights] = await Promise.all([loadRankings(point, maxDriveMinutes, null), fetchRankingCalendar(where)]);
      setCalendar(nights);
      setSearch({ point, maxDrive: maxDriveMinutes });
    } catch {
      setError("Couldn't get rankings from the server. Is the FastAPI back end running?");
    } finally {
      setLoading("");
    }
  }

  // Clicking a night in the calendar re-ranks the same search for that night.
  async function handlePickNight(night) {
    if (!search || night === rankings?.night) return;
    setError("");
    setLoading(`Ranking sites for ${formatNight(night)}...`);
    try {
      await loadRankings(search.point, search.maxDrive, night);
    } catch {
      setError("Couldn't load that night. Try again.");
    } finally {
      setLoading("");
    }
  }

  const results = rankings?.results;
  const changedSinceSearch = search && maxDriveMinutes !== search.maxDrive;

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

        <button type="submit" className="primary" disabled={Boolean(loading)}>
          {loading ? "Searching..." : "Find stargazing spots"}
        </button>
        {changedSinceSearch && <p className="note">Press the button again to update the results.</p>}
      </form>

      {/* role="status" makes screen readers announce loading and result messages */}
      <div role="status" aria-live="polite">
        {loading ? (
          <p className="loading">
            <span className="spinner" aria-hidden="true" /> {loading}
          </p>
        ) : (
          status && <p className="status">{status}</p>
        )}
      </div>
      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {results && calendar.length > 0 && (
        <section className="calendar-section">
          <h2>Pick a night</h2>
          <p className="note">The best score within your drive time each night. Click a night to rank it.</p>
          <NightCalendar
            nights={calendar}
            selectedNight={rankings.night}
            onSelect={handlePickNight}
            disabled={Boolean(loading)}
          />
        </section>
      )}

      <div className={results ? "results-layout" : undefined}>
        {results && (
          <section className="results-panel">
            <h2>Best spots for {formatNight(rankings.night, { weekday: "long", month: "short", day: "numeric" })}</h2>
            <p className="note">
              Ranked by the night&apos;s score, with a small penalty for longer drives.{" "}
              {rankings.drive_source === "openrouteservice"
                ? "Drive times are real driving routes."
                : "~ means the drive time is an estimate (real routing wasn't available)."}
            </p>
            <SiteList sites={results} night={rankings.night} selectedId={selectedId} onSelect={setSelectedId} />
          </section>
        )}

        {/* Before a search the map shows every site; after a search it shows only the ranked results. */}
        <MapView
          sites={results ?? allSites}
          startPoint={search?.point}
          ranked={Boolean(results)}
          night={rankings?.night}
          selectedId={selectedId}
          onSelect={results ? setSelectedId : undefined}
        />
      </div>

      {/* Site details (/sites/:siteId) open here, on top of the search page */}
      <Outlet />
    </main>
  );
}
