import type { ActionKind, Condition, ConditionKind, GeoPoint, Play, Polygon, RouteDef, Step } from "../../contracts.gen";

// Card editing (Part3-12.1). Each function returns a new play and leaves the input as it was.

// What the editor offers: the actions sim moves and the conditions runtime evaluates (search_area, watch_point,
// relay_comms, time_elapsed and signal_received do nothing in this simulator; a card that already has one keeps it).
export const EDIT_ACTIONS: ActionKind[] = ["patrol_route", "move_to", "watch_target", "approach_target", "strike_target", "hold", "return_home"];
export const EDIT_CONDITIONS: ConditionKind[] = ["target_found", "arrived", "battery_below", "operator_choice", "at_time"];
// Decision 0045: the editor shows move_to and patrol_route as one action, "경로 비행", with "반복" (looping).
export const ROUTE_KINDS: ActionKind[] = ["move_to", "patrol_route"];

// What the card panel offers. An enemy play keeps its script as it is (decision 0045): sim steers enemies by a
// move_to target or a patrol_route route only and reads arrived/time_elapsed, so no route select and no T+.
export function cardOptions(kind: ActionKind, enemy: boolean): { routeControls: boolean; conditions: ConditionKind[] } {
  return {
    routeControls: !enemy && ROUTE_KINDS.includes(kind),
    conditions: enemy ? EDIT_CONDITIONS.filter((k) => k !== "at_time") : EDIT_CONDITIONS,
  };
}
const TARGETED: ActionKind[] = ["watch_target", "approach_target", "strike_target"];
const DISTANCE: Partial<Record<ActionKind, number>> = { watch_target: 150, approach_target: 200 };

export function updateStep(play: Play, stepId: string, change: (s: Step) => Step): Play {
  return { ...play, steps: play.steps.map((s) => (s.id === stepId ? change(s) : s)) };
}

function isPoint(v: unknown): v is GeoPoint {
  return !!v && typeof v === "object" && "lat" in v && "lon" in v;
}
// A point for move_to / patrol_route, since the editor has no map: this step's own first, then the play's,
// then the fallback (the zone centre, for a play written from one empty card).
function pointFor(play: Play, stepId: string, fallback: GeoPoint | null): GeoPoint | null {
  const own = play.steps.filter((s) => s.id === stepId);
  for (const s of [...own, ...play.steps.filter((s) => s.id !== stepId)]) {
    const p = s.do.params ?? {};
    if (isPoint(p.target)) return p.target;
    if (Array.isArray(p.route) && isPoint(p.route[0])) return p.route[0];
  }
  return fallback;
}

export function zoneCentre(zone: Polygon): GeoPoint {
  const n = zone.points.length;
  return { lat: zone.points.reduce((a, p) => a + p.lat, 0) / n, lon: zone.points.reduce((a, p) => a + p.lon, 0) / n };
}

export function setActionKind(play: Play, stepId: string, kind: ActionKind, fallback: GeoPoint | null = null): Play {
  return updateStep(play, stepId, (s) => {
    if (s.do.kind === kind) return s;
    const old = s.do.params ?? {};
    let params: Record<string, unknown> = {};
    if (TARGETED.includes(kind)) {
      params.target = typeof old.target === "string" ? old.target : "nearest";
      if (kind !== "strike_target") params.distance_m = typeof old.distance_m === "number" ? old.distance_m : DISTANCE[kind];
    }
    const point = pointFor(play, stepId, fallback);
    if (kind === "move_to" && point) params = { target: point };
    if (kind === "patrol_route") params = Array.isArray(old.route) ? { route: old.route } : point ? { route: [point] } : {};
    return { ...s, do: { kind, params } };
  });
}

// A route from the list copied into the card: fixed points as `route`, a relative shape as `offsets`
// (runtime measures them from where the vehicle is when the card starts, decision 0044).
export function applyRoute(play: Play, stepId: string, route: RouteDef): Play {
  return updateStep(play, stepId, (s) => {
    const params = route.offsets?.length
      ? { offsets: route.offsets, route_name: route.name }
      : { route: route.points ?? [], route_name: route.name };
    return { ...s, do: { kind: s.do.kind, params } };
  });
}

// "반복": patrol_route loops, move_to follows the route once. The route stays; a point move gets a one-point route.
export function setLoop(play: Play, stepId: string, loop: boolean): Play {
  return updateStep(play, stepId, (s) => {
    const kind: ActionKind = loop ? "patrol_route" : "move_to";
    if (s.do.kind === kind) return s;
    const { target, ...rest } = s.do.params ?? {};
    const params = loop && !rest.route && !rest.offsets && isPoint(target) ? { ...rest, route: [target] } : { ...s.do.params };
    return { ...s, do: { kind, params } };
  });
}

// Which listed route the card holds (by its name), or "" when it holds another one (unnamed, a point move).
export function routeChoice(params: Record<string, unknown>, routes: RouteDef[]): string {
  return routes.find((r) => r.name === params.route_name)?.id ?? "";
}

export function defaultCondition(kind: ConditionKind, step: Step): Condition {
  if (kind === "battery_below") return { kind, params: { pct: 30 } };
  if (kind === "at_time") return { kind, params: { offset_ms: 60000 } };
  if (kind === "operator_choice") return { kind, params: { choice: step.report?.choices?.[0]?.id ?? "" } };
  return { kind, params: {} };
}

function freshId(taken: string[], prefix: string, start: number): string {
  let n = start;
  while (taken.includes(`${prefix}${n}`)) n++;
  return `${prefix}${n}`;
}

// A hold card right after the step, reached from it on arrival (the operator changes both as needed).
export function addStepAfter(play: Play, stepId: string): { play: Play; id: string } {
  const at = play.steps.findIndex((s) => s.id === stepId);
  if (at < 0) return { play, id: "" };
  const id = freshId(play.steps.map((s) => s.id), "step-", 1);
  const card: Step = { id, name: "새 카드", do: { kind: "hold", params: {} }, on: [], ui: {} };
  const linked = updateStep(play, stepId, (s) => ({ ...s, on: [...(s.on ?? []), { cond: { kind: "arrived", params: {} }, go_step: id }] }));
  return { play: { ...linked, steps: [...linked.steps.slice(0, at + 1), card, ...linked.steps.slice(at + 1)] }, id };
}

// Drops the step with every exit into it and an emergency link to it. The entry step stays.
export function removeStep(play: Play, stepId: string): Play {
  if (stepId === play.entry) return play;
  const em = { ...play.emergency };
  for (const k of ["link_lost_step", "battery_low_step", "operator_call_step"] as const) if (em[k] === stepId) em[k] = null;
  const steps = play.steps.filter((s) => s.id !== stepId).map((s) => ({ ...s, on: (s.on ?? []).filter((e) => e.go_step !== stepId) }));
  return { ...play, steps, emergency: em };
}

export function addChoice(play: Play, stepId: string): Play {
  return updateStep(play, stepId, (s) => {
    const choices = s.report?.choices ?? [];
    const id = freshId(choices.map((c) => c.id), "c", 1);
    return { ...s, report: { text: s.report?.text ?? "", choices: [...choices, { id, label: `선택 ${choices.length + 1}`, play_by_vehicle: {} }] } };
  });
}

// Removes a report choice and the operator_choice exit that waited for it.
export function removeChoice(play: Play, stepId: string, choiceId: string): Play {
  return updateStep(play, stepId, (s) => ({
    ...s,
    report: s.report && { ...s.report, choices: (s.report.choices ?? []).filter((c) => c.id !== choiceId) },
    on: (s.on ?? []).filter((e) => !(e.cond.kind === "operator_choice" && e.cond.params?.choice === choiceId)),
  }));
}
