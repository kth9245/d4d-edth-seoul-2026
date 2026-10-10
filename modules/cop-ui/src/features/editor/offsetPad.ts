import type { RouteOffset } from "../../contracts.gen";

export type OffsetPad = {
  half: number; // metres from the centre to each edge
  grid: number; // metres between grid lines
  toXY: (o: RouteOffset) => [number, number];
  fromXY: (x: number, y: number) => RouteOffset;
  labels: { at: [number, number]; text: string }[]; // one per spot: points on one spot read "1·2" (Part1-41)
};

// The relative route's drawing pad (Part1-40): a square of `size` px with the vehicle at the centre, north up.
// It shows at least 1 km each way and grows (in 500 m steps) so typed points stay on it; clicks snap to 10 m.
export function offsetPad(offsets: RouteOffset[], size: number): OffsetPad {
  const far = Math.max(0, ...offsets.flatMap((o) => [Math.abs(o.north_m), Math.abs(o.east_m)]));
  const half = Math.max(1000, Math.ceil((far * 1.1) / 500) * 500);
  const grid = half <= 1000 ? 100 : half <= 2500 ? 250 : 500;
  const c = size / 2;
  const snap = (m: number) => Math.round(m / 10) * 10 || 0;
  const toXY = (o: RouteOffset): [number, number] => [c + (o.east_m / half) * c, c - (o.north_m / half) * c];
  const spots = new Map<string, { at: [number, number]; numbers: number[] }>();
  offsets.forEach((o, i) => {
    const k = `${o.north_m},${o.east_m}`;
    if (!spots.has(k)) spots.set(k, { at: toXY(o), numbers: [] });
    spots.get(k)!.numbers.push(i + 1);
  });
  return {
    half,
    grid,
    toXY,
    fromXY: (x, y) => ({ north_m: snap(((c - y) / c) * half), east_m: snap(((x - c) / c) * half) }),
    labels: [...spots.values()].map((s) => ({ at: s.at, text: s.numbers.join("·") })),
  };
}
