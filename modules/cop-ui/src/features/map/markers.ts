import { type Map as MapLibreMap, Marker } from "maplibre-gl";
import type { GeoPoint } from "../../contracts.gen";
import type { TargetMarker, VehicleMarker } from "./frameMarkers";

export type MarkerStore = Map<string, Marker>;

// Keep one HTML marker per id: create new ones, move existing ones, remove the ones that left the frame.
// MapLibre owns the classes of the outer element, so the style classes go on an inner element.
// A marker with onClick swallows its own mouse events so the click never reaches the map as a map click.
function sync<T extends { id: string; lon: number; lat: number }>(
  map: MapLibreMap, store: MarkerStore, items: T[], cls: (item: T) => string, onClick?: (id: string) => void,
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
      if (onClick) {
        const id = item.id;
        for (const type of ["mousedown", "mouseup", "dblclick"]) outer.addEventListener(type, (e) => e.stopPropagation());
        outer.addEventListener("click", (e) => {
          e.stopPropagation();
          onClick(id);
        });
      }
      mk = new Marker({ element: outer }).setLngLat([item.lon, item.lat]).addTo(map);
      store.set(item.id, mk);
    }
    mk.setLngLat([item.lon, item.lat]);
    (mk.getElement().firstChild as HTMLElement).className = cls(item);
  }
}

export function syncVehicles(map: MapLibreMap, store: MarkerStore, items: VehicleMarker[],
  selected: string | null, onClick: (id: string) => void): void {
  sync(map, store, items, (v) => `mk vehicle ${v.status}${v.id === selected ? " selected" : ""}`, onClick);
}

export function syncTargets(map: MapLibreMap, store: MarkerStore, items: TargetMarker[]): void {
  sync(map, store, items, (t) => `mk target ${t.kind}${t.seen ? "" : " unseen"}`);
}

// Where the last direct-control order was sent (a cross), so the operator sees the order land.
export function syncAim(map: MapLibreMap, store: MarkerStore, aim: (GeoPoint & { label: string }) | null): void {
  sync(map, store, aim ? [{ id: aim.label, lat: aim.lat, lon: aim.lon }] : [], () => "mk aim");
}

export function clearMarkers(store: MarkerStore): void {
  store.forEach((mk) => mk.remove());
  store.clear();
}
