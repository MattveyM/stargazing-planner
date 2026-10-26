import { formatMinutes } from "../utils/distance";

// Shows a table of dark-sky sites. Each site may include distance and drive-time estimates.
export default function SiteList({ sites }) {
  if (sites.length === 0) {
    return <p className="empty">No sites found within that drive time. Try a longer drive.</p>;
  }

  return (
    <table className="site-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Site</th>
          <th>Region</th>
          <th>Est. drive</th>
          <th>Sky darkness</th>
          <th>Road access</th>
        </tr>
      </thead>
      <tbody>
        {sites.map((site, index) => (
          <tr key={site.id}>
            <td>{index + 1}</td>
            <td className="site-name">{site.name}</td>
            <td>
              {site.region}, {site.state}
            </td>
            <td>{site.driveMinutes != null ? formatMinutes(site.driveMinutes) : "-"}</td>
            <td>Bortle {site.bortle}</td>
            <td>{site.road_access}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
