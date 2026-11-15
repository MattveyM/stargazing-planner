// Marker colors by sky darkness (Bortle scale: 1 = darkest, 9 = city).
// Before a search the map colors sites by Bortle; after a search it colors them by the night's score.
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

// Map legend for search results (same colors and words as scoreLevel)
export const SCORE_LEVELS = [
  { label: "Great (70+)", color: "#1a7f37" },
  { label: "Fair (45-69)", color: "#8a6510" },
  { label: "Poor (under 45)", color: "#b42318" },
  { label: "No score yet", color: "#8b95a7" },
];

export function scoreColor(score) {
  return score == null ? "#8b95a7" : scoreLevel(score).color;
}
