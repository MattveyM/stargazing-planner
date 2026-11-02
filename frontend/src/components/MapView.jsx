import { useEffect } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { formatMinutes } from "../utils/distance";
import { SKY_LEVELS, bortleColor } from "../utils/skyColors";

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

export default function MapView({ sites, startPoint }) {
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

        {sites.map((site) => (
          <CircleMarker
            key={site.id}
            center={[site.latitude, site.longitude]}
            radius={9}
            pathOptions={{ color: "#ffffff", weight: 2, fillColor: bortleColor(site.bortle), fillOpacity: 0.9 }}
          >
            <Popup>
              <strong>{site.name}</strong>
              <br />
              {site.region}, {site.state}
              <br />
              Sky darkness: Bortle {site.bortle} · Road: {site.road_access}
              {site.driveMinutes != null && (
                <>
                  <br />
                  Est. drive: {formatMinutes(site.driveMinutes)}
                </>
              )}
              {site.notes && <p className="popup-notes">{site.notes}</p>}
            </Popup>
          </CircleMarker>
        ))}

        <FitToResults sites={sites} startPoint={startPoint} />
      </MapContainer>

      <div className="map-legend">
        {SKY_LEVELS.map((level) => (
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
