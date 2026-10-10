import type { CapabilityReason, Ontology, OntologyView, Operation, Play, VehicleSpec } from "../../contracts.gen";

export interface KindRow { id: string; label: string; depth: number; adds: string; vehicles: string[] }

// The kind hierarchy as indented rows, each parent before its children, in the ontology's order (decision 0038).
export function kindRows(onto: Ontology, vehicles: VehicleSpec[]): KindRow[] {
  const groupLabel = new Map(onto.groups.map((g) => [g.id, g.label]));
  const rows: KindRow[] = [];
  const walk = (parent: string | null, depth: number) => {
    for (const k of onto.kinds.filter((x) => (x.is_a ?? null) === parent)) {
      rows.push({ id: k.id, label: k.label, depth, adds: (k.provides ?? []).map((p) => groupLabel.get(p) ?? p).join("·"),
        vehicles: vehicles.filter((v) => v.kind === k.id).map((v) => v.id) });
      walk(k.id, depth + 1);
    }
  };
  walk(null, 0);
  return rows;
}

// Why a vehicle can or cannot run one action: the kinds the server walked and what gave it.
export function reasonLine(r: CapabilityReason, onto: Ontology): string {
  const label = new Map(onto.kinds.map((k) => [k.id, k.label]));
  const path = r.path.map((id) => label.get(id) ?? id).join(" → ");
  if (!r.allowed) return `${path}, 어디에도 없음`;
  const group = onto.groups.find((g) => g.id === r.via);
  return `${path} (${group ? `${group.label} 묶음` : r.via})`;
}

// Actions of the plays a vehicle may be given: its start play, switch buttons and report choices naming it.
function actionsFor(vid: string, op: Operation, plays: Play[]): string[] {
  const ids = new Set<string>();
  if (op.assign?.[vid]) ids.add(op.assign[vid]);
  for (const sw of op.switches ?? []) if (sw.play_by_vehicle[vid]) ids.add(sw.play_by_vehicle[vid]);
  for (const p of plays) for (const s of p.steps) for (const c of s.report?.choices ?? []) {
    if (c.play_by_vehicle?.[vid]) ids.add(c.play_by_vehicle[vid]);
  }
  return [...new Set(plays.filter((p) => ids.has(p.id)).flatMap((p) => p.steps.map((s) => s.do.kind as string)))];
}

// One line per reserve; shown only, the engine's reserve choice is unchanged (decision 0038).
export function reserveLines(op: Operation, plays: Play[], view: OntologyView, vehicles: VehicleSpec[]): string[] {
  const kindOf = new Map(vehicles.map((v) => [v.id, v.kind ?? null]));
  const kindLabel = new Map(view.ontology.kinds.map((k) => [k.id, k.label]));
  const can = new Map(view.vehicles.map((v) => [v.vehicle_id, new Set<string>(v.reasons.filter((r) => r.allowed).map((r) => r.action))]));
  return Object.entries(op.reserve ?? {}).flatMap(([vid, reserves]) => {
    const need = actionsFor(vid, op, plays);
    return reserves.map((r) => {
      const missing = need.filter((a) => !can.get(r)?.has(a));
      if (missing.length) return `${r}는 ${vid}의 예비. ${vid}의 플레이가 쓰는 행동 중 ${missing.join("·")}를 ${r}가 못 함`;
      const kr = kindOf.get(r);
      const kind = kr && kr === kindOf.get(vid) ? `같은 ${kindLabel.get(kr)}` : `${r}: ${kindLabel.get(kr ?? "") ?? "종류 없음"}`;
      return `${r}는 ${vid}의 예비. ${vid}의 플레이가 쓰는 행동 ${need.length}개를 ${r}가 모두 할 수 있음(${kind})`;
    });
  });
}
