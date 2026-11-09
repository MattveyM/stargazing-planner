import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import { Line } from "react-chartjs-2";
import { formatHour } from "../utils/time";

// Chart.js only includes the pieces you register (keeps the app smaller).
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

// One color + one dash style per cloud layer, so the lines can be told apart without color.
const LAYERS = [
  { key: "cloud_low", label: "Low clouds (block the most)", color: "#2a78d6", dash: [] },
  { key: "cloud_mid", label: "Mid clouds", color: "#eb6834", dash: [8, 5] },
  { key: "cloud_high", label: "High clouds (thin)", color: "#1baf7a", dash: [2, 4] },
];

// Hourly cloud cover (%) for the hours of one night.
export default function CloudChart({ hours }) {
  if (hours.length === 0) {
    return <p className="empty">No hourly forecast saved for this night yet.</p>;
  }

  const data = {
    labels: hours.map((h) => formatHour(h.forecast_hour)),
    datasets: LAYERS.map((layer) => ({
      label: layer.label,
      data: hours.map((h) => h[layer.key]),
      borderColor: layer.color,
      backgroundColor: layer.color,
      borderDash: layer.dash,
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 5,
      tension: 0.3,
    })),
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false }, // hover anywhere in a column to see all 3 values
    plugins: {
      legend: { position: "bottom", labels: { usePointStyle: false, boxWidth: 28, color: "#333" } },
      tooltip: { callbacks: { label: (item) => ` ${item.dataset.label}: ${item.parsed.y}%` } },
    },
    scales: {
      y: {
        min: 0,
        max: 100,
        title: { display: true, text: "Cloud cover (%)", color: "#555" },
        ticks: { stepSize: 25, color: "#555" },
        grid: { color: "#ececec" },
      },
      x: { ticks: { color: "#555", maxRotation: 0, autoSkip: true }, grid: { display: false } },
    },
  };

  return (
    <div className="cloud-chart" role="img" aria-label="Hourly cloud cover for this night, by cloud layer">
      <Line data={data} options={options} />
    </div>
  );
}
