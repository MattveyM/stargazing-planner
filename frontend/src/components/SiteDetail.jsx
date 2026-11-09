import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { fetchForecast, fetchNights, fetchSite } from "../api";
import { scoreLevel } from "../utils/skyColors";
import { formatNight, formatTime } from "../utils/time";
import CloudChart from "./CloudChart";
import "./SiteDetail.css";

// The four parts of the 0-100 score and how many points each is worth.
const PARTS = [
  { key: "cloud_score", label: "Clouds", max: 50 },
  { key: "moon_score", label: "Moonlight", max: 20 },
  { key: "darkness_score", label: "Hours of darkness", max: 15 },
  { key: "light_score", label: "Light pollution", max: 15 },
];

const HOUR = 60 * 60 * 1000;

export default function SiteDetail() {
  const { siteId } = useParams(); // from the URL: /sites/12
  const navigate = useNavigate();
  const [site, setSite] = useState(null);
  const [nights, setNights] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [selectedNight, setSelectedNight] = useState(null);
  const [error, setError] = useState("");

  // Load the site, its 7 nightly scores, and its hourly forecast at the same time.
  useEffect(() => {
    Promise.all([fetchSite(siteId), fetchNights(siteId), fetchForecast(siteId)])
      .then(([siteData, nightData, forecastData]) => {
        setSite(siteData);
        setNights(nightData);
        setForecast(forecastData);
        // Start on the best night of the week
        const best = nightData.reduce((a, b) => (b.score > a.score ? b : a), nightData[0]);
        setSelectedNight(best ? best.night : null);
      })
      .catch((err) =>
        setError(err.message === "Not found" ? "That site doesn't exist." : "Can't reach the server."),
      );
  }, [siteId]);

  // Close with the Escape key, like most pop-up windows.
  useEffect(() => {
    const onKey = (event) => event.key === "Escape" && navigate("/");
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [navigate]);

  const night = nights.find((n) => n.night === selectedNight);
  const best = nights.length ? Math.max(...nights.map((n) => n.score)) : null;

  // The chart shows the dark hours, plus one hour on each side.
  const nightHours = night?.dark_start
    ? forecast.filter((h) => {
        const t = new Date(h.forecast_hour).getTime();
        return t >= new Date(night.dark_start).getTime() - HOUR && t <= new Date(night.dark_end).getTime() + HOUR;
      })
    : [];

  return (
    <div className="detail-backdrop" onClick={() => navigate("/")}>
      <article className="detail-panel" onClick={(e) => e.stopPropagation()} aria-labelledby="site-title">
        <button className="close-button" onClick={() => navigate("/")} aria-label="Close site details">
          ✕
        </button>

        {error && <p className="error">{error}</p>}
        {!site && !error && <p>Loading…</p>}

        {site && (
          <>
            <header className="detail-header">
              <h2 id="site-title">{site.name}</h2>
              <p className="detail-meta">
                {site.region}, {site.state} · Sky darkness: Bortle {site.bortle} · Road: {site.road_access}
              </p>
              {site.notes && <p className="detail-notes">{site.notes}</p>}
            </header>

            {nights.length === 0 ? (
              <p className="empty">No scores yet. Run the scoring job: python -m jobs.score_nights</p>
            ) : (
              <>
                <h3>Next 7 nights</h3>
                <div className="night-strip" role="list">
                  {nights.map((n) => {
                    const level = scoreLevel(n.score);
                    return (
                      <button
                        key={n.night}
                        role="listitem"
                        className={`night-card ${n.night === selectedNight ? "selected" : ""}`}
                        style={{ background: level.background }}
                        onClick={() => setSelectedNight(n.night)}
                        aria-pressed={n.night === selectedNight}
                      >
                        <span className="night-date">{formatNight(n.night)}</span>
                        <span className="night-score" style={{ color: level.color }}>
                          {n.score}
                        </span>
                        <span className="night-label">
                          {level.label}
                          {n.score === best ? " · Best" : ""}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {night && (
                  <section className="night-detail">
                    <div className="score-box">
                      <p className="score-title">
                        {formatNight(night.night, { weekday: "long", month: "long", day: "numeric" })}
                      </p>
                      <p className="score-big" style={{ color: scoreLevel(night.score).color }}>
                        {night.score}
                        <span>/100</span>
                      </p>
                      <p className="score-label">{scoreLevel(night.score).label} night for stargazing</p>
                    </div>

                    <div className="breakdown">
                      <h3>Why this score</h3>
                      {PARTS.map((part) => (
                        <div key={part.key} className="part-row">
                          <span className="part-label">{part.label}</span>
                          <span className="part-bar">
                            <span style={{ width: `${(100 * night[part.key]) / part.max}%` }} />
                          </span>
                          <span className="part-value">
                            {night[part.key]} / {part.max}
                          </span>
                        </div>
                      ))}
                    </div>

                    <ul className="facts">
                      <li>
                        <strong>Fully dark:</strong> {formatTime(night.dark_start)} – {formatTime(night.dark_end)} (
                        {night.dark_hours} hrs)
                      </li>
                      <li>
                        <strong>Moon:</strong> {night.moon_percent}% lit
                      </li>
                      <li>
                        <strong>Clouds blocking the sky:</strong> {night.avg_cloud}% on average
                      </li>
                    </ul>

                    <h3>Hourly clouds that night</h3>
                    <CloudChart hours={nightHours} />
                  </section>
                )}
              </>
            )}
          </>
        )}
      </article>
    </div>
  );
}
