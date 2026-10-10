import { type Map as MapLibreMap, Marker } from "maplibre-gl";
import type { Aim } from "./directAims";
import type { TargetMarker, VehicleMarker } from "./frameMarkers";

export type MarkerStore = Map<string, Marker>;

// Keep one HTML marker per id: create new ones, move existing ones, remove the ones that left the frame.
// MapLibre owns the classes of the outer element, so the style classes go on an inner element.
// A marker with onClick swallows its own mouse events so the click never reaches the map as a map click.
// The label is the item's label (or its id) and is rewritten every frame, e.g. "fast1 · 무력화" once struck.
function sync<T extends { id: string; lon: number; lat: number; label?: string }>(
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
      inner.appendChild(document.createElement("span"));
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
    const inner = mk.getElement().firstChild as HTMLElement;
    inner.className = cls(item);
    inner.lastChild!.textContent = item.label ?? item.id;
  }
}

export function syncVehicles(map: MapLibreMap, store: MarkerStore, items: VehicleMarker[],
  selected: string | null, onClick: (id: string) => void): void {
  sync(map, store, items, (v) => `mk vehicle ${v.status} batt-${v.battery}${v.id === selected ? " selected" : ""}`, onClick);
}

// Target classes carry what our side knows (track: seen, rf, lost, never, gone) and the risk tone (Part1-32).
// onClick is for pointing (decision 0048); target markers ignore the mouse otherwise (index.css).
export function syncTargets(map: MapLibreMap, store: MarkerStore, items: TargetMarker[], onClick?: (id: string) => void): void {
  sync(map, store, items,
    (t) => `mk target ${t.kind} ${t.track} ${t.tone}${t.seen ? "" : " unseen"}${t.neutralized ? " neutralized" : ""}${t.rf ? " rf" : ""}`,
    onClick);
}

// Where direct-control orders are heading (a cross per vehicle), so the operator sees the order land.
export function syncAim(map: MapLibreMap, store: MarkerStore, aims: Aim[]): void {
  sync(map, store, aims.map((a) => ({ id: a.label, lat: a.lat, lon: a.lon })), () => "mk aim");
}

export function clearMarkers(store: MarkerStore): void {
  store.forEach((mk) => mk.remove());
  store.clear();
}
