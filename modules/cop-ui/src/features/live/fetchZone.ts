import type { Operation, Polygon } from "../../contracts.gen";

// The zone is set once when the operation is created (Part1-9 decision), so the screen reads it once at start.
// Any failure (old gateway without /operation, network) means "draw no zone", never a broken screen.
export async function fetchZone(): Promise<Polygon | null> {
  try {
    const r = await fetch("/operation");
    if (!r.ok) return null;
    const op = (await r.json()) as Partial<Operation>;
    return Array.isArray(op.zone?.points) ? op.zone : null;
  } catch {
    return null;
  }
}
