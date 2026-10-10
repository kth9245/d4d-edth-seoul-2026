import { type Map as MapLibreMap, Marker } from "maplibre-gl";
import type { TargetMarker, VehicleMarker } from "./frameMarkers";

export type MarkerStore = Map<string, Marker>;

// Keep one HTML marker per id: create new ones, move existing ones, remove the ones that left the frame.
// MapLibre owns the classes of the outer element, so the style classes go on an inner element.
function sync<T extends { id: string; lon: number; lat: number }>(
  map: MapLibreMap, store: MarkerStore, items: T[], cls: (item: T) => string,
): void {
  const ids = new Set(items.map((i) => i.id));
  for (const [id, mk] of store) {
    if (!ids.has(id)) {
      mk.remove();
      store.delete(id);
    }
  }
  for (const item of items) {
    let mk = store.get(item.id);
    if (!mk) {
      const outer = document.createElement("div");
      const inner = outer.appendChild(document.createElement("div"));
      inner.appendChild(document.createElement("i"));
      inner.appendChild(document.createElement("span")).textContent = item.id;
      mk = new Marker({ element: outer }).setLngLat([item.lon, item.lat]).addTo(map);
      store.set(item.id, mk);
    }
    mk.setLngLat([item.lon, item.lat]);
    (mk.getElement().firstChild as HTMLElement).className = cls(item);
  }
}

export function syncVehicles(map: MapLibreMap, store: MarkerStore, items: VehicleMarker[]): void {
  sync(map, store, items, (v) => `mk vehicle ${v.status}`);
}

export function syncTargets(map: MapLibreMap, store: MarkerStore, items: TargetMarker[]): void {
  sync(map, store, items, (t) => `mk target ${t.kind}${t.seen ? "" : " unseen"}`);
}

export function clearMarkers(store: MarkerStore): void {
  store.forEach((mk) => mk.remove());
  store.clear();
}
