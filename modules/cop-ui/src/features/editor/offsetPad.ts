import type { RouteOffset } from "../../contracts.gen";

export type OffsetPad = {
  half: number; // metres from the centre to each edge
  grid: number; // metres between grid lines
  toXY: (o: RouteOffset) => [number, number];
  fromXY: (x: number, y: number) => RouteOffset;
};

// The relative route's drawing pad (Part1-40): a square of `size` px with the vehicle at the centre, north up.
// It shows at least 1 km each way and grows (in 500 m steps) so typed points stay on it; clicks snap to 10 m.
export function offsetPad(offsets: RouteOffset[], size: number): OffsetPad {
  const far = Math.max(0, ...offsets.flatMap((o) => [Math.abs(o.north_m), Math.abs(o.east_m)]));
  const half = Math.max(1000, Math.ceil((far * 1.1) / 500) * 500);
  const grid = half <= 1000 ? 100 : half <= 2500 ? 250 : 500;
  const c = size / 2;
  const snap = (m: number) => Math.round(m / 10) * 10 || 0;
  return {
    half,
    grid,
    toXY: (o) => [c + (o.east_m / half) * c, c - (o.north_m / half) * c],
    fromXY: (x, y) => ({ north_m: snap(((c - y) / c) * half), east_m: snap(((x - c) / c) * half) }),
  };
}
