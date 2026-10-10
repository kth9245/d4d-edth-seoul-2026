import type { GeoPoint, RouteDef, RouteOffset } from "../../contracts.gen";

// "＋ 경로 추가" (decision 0054): a fixed route keeps the points clicked on the map (5 decimals, about 1 m);
// a relative route keeps north/east metres from where the vehicle is as the card starts (whole metres).
export function newRoute(name: string, kind: "fixed" | "relative", points: GeoPoint[], offsets: RouteOffset[], existingIds: string[]): RouteDef {
  const taken = new Set(existingIds);
  let id = "new_route";
  for (let n = 2; taken.has(id); n++) id = `new_route-${n}`;
  const r5 = (x: number) => Math.round(x * 1e5) / 1e5;
  return {
    id,
    name: name.trim() || "새 경로",
    points: kind === "fixed" ? points.map((p) => ({ lat: r5(p.lat), lon: r5(p.lon), alt_m: 0 })) : [],
    offsets: kind === "relative" ? offsets.map((o) => ({ north_m: Math.round(o.north_m), east_m: Math.round(o.east_m) })) : [],
  };
}
