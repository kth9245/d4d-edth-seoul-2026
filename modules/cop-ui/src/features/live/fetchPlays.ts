import type { Play } from "../../contracts.gen";

// GET /plays for the switch panel. Any failure is an empty list, never a broken screen.
export async function fetchPlays(): Promise<Play[]> {
  try {
    const r = await fetch("/plays");
    if (!r.ok) return [];
    const data = await r.json();
    return Array.isArray(data) ? (data as Play[]) : [];
  } catch {
    return [];
  }
}
