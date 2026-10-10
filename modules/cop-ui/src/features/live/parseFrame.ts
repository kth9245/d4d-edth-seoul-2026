import type { Frame } from "../../contracts.gen";

// One /ws message → Frame. Broken messages and the old gateway's LegacyFrame (no vehicles) are dropped.
export function parseFrame(data: string): Frame | null {
  try {
    const f = JSON.parse(data) as Partial<Frame> | null;
    if (!f || typeof f !== "object" || !Array.isArray(f.vehicles) || !Array.isArray(f.targets)) return null;
    return f as Frame;
  } catch {
    return null;
  }
}
