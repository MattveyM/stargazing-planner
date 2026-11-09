// Marker colors by sky darkness (Bortle scale: 1 = darkest, 9 = city).
// Later these will switch to the nightly 0-100 score.
export const SKY_LEVELS = [
  { label: "Very dark (Bortle 1-2)", color: "#1a7f37", test: (b) => b <= 2 },
  { label: "Dark (Bortle 3)", color: "#bf8700", test: (b) => b === 3 },
  { label: "Some light pollution (Bortle 4+)", color: "#cf222e", test: (b) => b >= 4 },
];

export function bortleColor(bortle) {
  return SKY_LEVELS.find((level) => level.test(bortle)).color;
}

// Nightly score levels (0-100). Each comes with a word so color is never the only signal.
export function scoreLevel(score) {
  if (score >= 70) return { label: "Great", color: "#1a7f37", background: "#e3f2e8" };
  if (score >= 45) return { label: "Fair", color: "#8a6510", background: "#fbf0d6" };
  return { label: "Poor", color: "#b42318", background: "#fbe4e2" };
}
