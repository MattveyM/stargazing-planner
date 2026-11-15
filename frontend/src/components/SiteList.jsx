import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { formatDrive } from "../utils/distance";
import { scoreLevel } from "../utils/skyColors";

// The ranked results. Clicking a row selects that site on the map; selecting a marker highlights its row.
export default function SiteList({ sites, night, selectedId, onSelect }) {
  const rowRefs = useRef({});

  // When a site is picked on the map, scroll its row into view.
  useEffect(() => {
    const row = rowRefs.current[selectedId];
    if (row) row.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [selectedId]);

  if (sites.length === 0) {
    return <p className="empty">No sites found within that drive time. Try a longer drive.</p>;
  }

  return (
    <div className="table-scroll">
      <table className="site-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Site</th>
            <th>Score</th>
            <th>Drive</th>
            <th>Sky</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {sites.map((site) => {
            const level = site.score != null ? scoreLevel(site.score) : null;
            const selected = site.id === selectedId;
            return (
              <tr
                key={site.id}
                ref={(el) => (rowRefs.current[site.id] = el)}
                className={selected ? "selected" : undefined}
                onClick={() => onSelect(site.id)}
              >
                <td>{site.rank}</td>
                <td>
                  {/* A real button so keyboard users can select rows too (its click reaches the row) */}
                  <button type="button" className="row-select" aria-pressed={selected}>
                    {site.name}
                  </button>
                  <div className="site-region">
                    {site.region}, {site.state}
                  </div>
                </td>
                <td>
                  {level ? (
                    <span className="score-pill" style={{ background: level.background, color: level.color }}>
                      {site.score} {level.label}
                    </span>
                  ) : (
                    <span className="score-pill none">No score</span>
                  )}
                </td>
                <td>{formatDrive(site)}</td>
                <td>Bortle {site.bortle}</td>
                <td>
                  <Link to={`/sites/${site.id}?night=${night}`} onClick={(e) => e.stopPropagation()}>
                    Details
                  </Link>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
