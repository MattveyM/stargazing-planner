import { useEffect, useRef } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";
import { Link } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import { formatDrive } from "../utils/distance";
import { SCORE_LEVELS, SKY_LEVELS, bortleColor, scoreColor, scoreLevel } from "../utils/skyColors";

const PNW_CENTER = [45.9, -120.6]; // middle of Washington + Oregon
const PNW_ZOOM = 6;

// Moves the map to show the search results. (react-leaflet's useMap gives access to the Leaflet map.)
function FitToResults({ sites, startPoint }) {
  const map = useMap();
  useEffect(() => {
    if (!startPoint) return; // no search yet: keep the whole-region view
    const points = [
      [startPoint.latitude, startPoint.longitude],
      ...sites.map((site) => [site.latitude, site.longitude]),
    ];
    if (points.length === 1) {
      map.setView(points[0], 8); // no sites in range: just center on the start
    } else {
      map.fitBounds(points, { padding: [40, 40] });
    }
  }, [map, sites, startPoint]);
  return null;
}

// Leaflet measures its box once. When the results layout puts the map beside the list (so the box
// changes size), tell Leaflet to measure again, or markers and pop-ups end up in the wrong place.
function KeepSizeCorrect() {
  const map = useMap();
  useEffect(() => {
    const observer = new ResizeObserver(() => map.invalidateSize());
    observer.observe(map.getContainer());
    return () => observer.disconnect();
  }, [map]);
  return null;
}

// When a row in the list is selected, open that marker's pop-up (and pan to it if it's off screen).
function ShowSelected({ selectedId, markerRefs }) {
  const map = useMap();
  useEffect(() => {
    const marker = markerRefs.current[selectedId];
    if (!marker) return;
    marker.bringToFront();
    if (!map.getBounds().contains(marker.getLatLng())) map.panTo(marker.getLatLng());
    marker.openPopup();
  }, [map, selectedId, markerRefs]);
  return null;
}

export default function MapView({ sites, startPoint, ranked = false, night, selectedId, onSelect }) {
  const markerRefs = useRef({});
  const legend = ranked ? SCORE_LEVELS : SKY_LEVELS;

  return (
    <div className="map-wrapper">
      <MapContainer center={PNW_CENTER} zoom={PNW_ZOOM} className="map">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {startPoint && (
          <CircleMarker
            center={[startPoint.latitude, startPoint.longitude]}
            radius={8}
            pathOptions={{ color: "#ffffff", weight: 3, fillColor: "#2563eb", fillOpacity: 1 }}
          >
            <Popup>Starting point: {startPoint.label}</Popup>
          </CircleMarker>
        )}

        {sites.map((site) => {
          const selected = site.id === selectedId;
          // After a search, color by tonight's (or the picked night's) score; before, by sky darkness.
          const fill = ranked ? scoreColor(site.score) : bortleColor(site.bortle);
          return (
            <CircleMarker
              key={site.id}
              ref={(layer) => (markerRefs.current[site.id] = layer)}
              center={[site.latitude, site.longitude]}
              radius={selected ? 13 : 9}
              pathOptions={{
                color: selected ? "#1f2a44" : "#ffffff",
                weight: selected ? 4 : 2,
                fillColor: fill,
                fillOpacity: 0.9,
              }}
              eventHandlers={onSelect ? { click: () => onSelect(site.id) } : undefined}
            >
              <Popup>
                <strong>
                  {site.rank ? `#${site.rank} ` : ""}
                  {site.name}
                </strong>
                <br />
                {site.region}, {site.state}
                {ranked && (
                  <>
                    <br />
                    Score: {site.score != null ? `${site.score} (${scoreLevel(site.score).label})` : "not scored yet"} ·
                    Drive: {formatDrive(site)}
                  </>
                )}
                <br />
                Sky darkness: Bortle {site.bortle} · Road: {site.road_access}
                {site.notes && <p className="popup-notes">{site.notes}</p>}
                <Link className="popup-link" to={night ? `/sites/${site.id}?night=${night}` : `/sites/${site.id}`}>
                  View 7-night forecast →
                </Link>
              </Popup>
            </CircleMarker>
          );
        })}

        <KeepSizeCorrect />
        <FitToResults sites={sites} startPoint={startPoint} />
        <ShowSelected selectedId={selectedId} markerRefs={markerRefs} />
      </MapContainer>

      <div className="map-legend">
        {legend.map((level) => (
          <span key={level.label}>
            <span className="legend-dot" style={{ background: level.color }} /> {level.label}
          </span>
        ))}
        <span>
          <span className="legend-dot" style={{ background: "#2563eb" }} /> Your starting point
        </span>
      </div>
    </div>
  );
}
