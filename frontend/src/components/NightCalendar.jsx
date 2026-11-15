import { scoreLevel } from "../utils/skyColors";
import { formatNight } from "../utils/time";

// A row of the next 7 nights. Each shows the best score near you that night; click one to rank that night.
export default function NightCalendar({ nights, selectedNight, onSelect, disabled }) {
  if (!nights.length) return null;
  const bestOfWeek = Math.max(...nights.map((n) => n.best_score ?? -1));

  return (
    <div className="calendar" role="group" aria-label="Pick a night">
      {nights.map((night, index) => {
        const level = night.best_score != null ? scoreLevel(night.best_score) : null;
        const selected = night.night === selectedNight;
        return (
          <button
            key={night.night}
            type="button"
            className={`calendar-day${selected ? " selected" : ""}`}
            style={level ? { background: level.background, color: level.color } : undefined}
            aria-pressed={selected}
            disabled={disabled}
            onClick={() => onSelect(night.night)}
            title={night.best_site_name ? `Best: ${night.best_site_name}` : "No scores yet"}
          >
            <span className="calendar-date">{index === 0 ? "Tonight" : formatNight(night.night)}</span>
            <span className="calendar-score">{night.best_score ?? "–"}</span>
            <span className="calendar-label">
              {level ? level.label : "No score"}
              {night.best_score === bestOfWeek && night.best_score >= 0 ? " · Best" : ""}
            </span>
            <span className="calendar-site">{night.best_site_name ?? ""}</span>
          </button>
        );
      })}
    </div>
  );
}
