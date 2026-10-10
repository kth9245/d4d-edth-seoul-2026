import { describe, expect, it } from "vitest";
import { newRoute } from "./newRoute";
import { postRoute } from "./postRoute";
import { routeGeoJSON } from "./routeGeoJSON";

const reply = (body: unknown, status = 200) => Promise.resolve(new Response(JSON.stringify(body), { status }));

describe("route add (decision 0054)", () => {
  it("a fixed route keeps the clicked points, rounded, with a free id", () => {
    const r = newRoute("  북쪽 해안  ", "fixed", [{ lat: 37.9612345, lon: 124.6612345, alt_m: 0 }], [], ["new_route"]);
    expect(r).toEqual({ id: "new_route-2", name: "북쪽 해안", points: [{ lat: 37.96123, lon: 124.66123, alt_m: 0 }], offsets: [] });
  });
  it("a relative route keeps the north and east metres, whole", () => {
    const r = newRoute("", "relative", [], [{ north_m: 200.4, east_m: -99.6 }], []);
    expect(r).toEqual({ id: "new_route", name: "새 경로", points: [], offsets: [{ north_m: 200, east_m: -100 }] });
  });
  it("draws the clicked points as numbered dots and a line once there are two", () => {
    const one = routeGeoJSON([{ lat: 1, lon: 2, alt_m: 0 }]);
    expect(one.features.map((f) => f.geometry.type)).toEqual(["Point"]);
    const two = routeGeoJSON([{ lat: 1, lon: 2, alt_m: 0 }, { lat: 3, lon: 4, alt_m: 0 }]);
    expect(two.features.map((f) => f.geometry.type)).toEqual(["LineString", "Point", "Point"]);
    expect(two.features[2].properties).toEqual({ n: "2" });
  });
  it("posts the route and returns the server's list", async () => {
    const route = { id: "new_route", name: "A", points: [], offsets: [{ north_m: 1, east_m: 0 }] };
    const seen: { url: string; init?: RequestInit }[] = [];
    expect(await postRoute(route, (url, init) => (seen.push({ url, init }), reply([route])))).toEqual([route]);
    expect(seen[0].url).toBe("/routes");
    expect(JSON.parse(String(seen[0].init?.body))).toEqual(route);
    await expect(postRoute(route, () => reply({}, 422))).rejects.toThrow("422");
  });
});
