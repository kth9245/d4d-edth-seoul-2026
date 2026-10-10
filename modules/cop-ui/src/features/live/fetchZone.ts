import type { Polygon } from "../../contracts.gen";
import { fetchOperation } from "./fetchOperation";

// The zone is set once when the operation is created (Part1-9 decision), so the screen reads it once at start.
// Any failure (old gateway without /operation, network) means "draw no zone", never a broken screen.
export async function fetchZone(): Promise<Polygon | null> {
  const op = await fetchOperation();
  return op?.zone && Array.isArray(op.zone.points) ? op.zone : null;
}
