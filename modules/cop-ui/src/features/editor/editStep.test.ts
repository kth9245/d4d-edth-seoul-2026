import { describe, expect, it } from "vitest";
import type { Role, RouteDef } from "../../contracts.gen";
import { addChoice, addStepAfter, applyRoute, cardOptions, defaultCondition, removeChoice, removeStep, routeChoice, setActionKind, setLoop, updateStep,
  zoneCentre } from "./editStep";

const role: Role = {
  id: "p", name: "순찰", domains: ["air"], entry: "patrol", origin: "human", approved: true, template: false,
  emergency: { battery_low_pct: 30, battery_low_step: "home" },
  steps: [
    { id: "patrol", name: "순찰", do: { kind: "patrol_route", params: { route: [{ lat: 37.9, lon: 124.6 }, { lat: 37.95, lon: 124.65 }] } },
      on: [{ cond: { kind: "target_found", params: {} }, go_step: "report" }], ui: {} },
    { id: "report", name: "보고", do: { kind: "hold", params: {} },
      on: [{ cond: { kind: "operator_choice", params: { choice: "go" } }, go_step: "watch" }],
      report: { text: "표적 발견", choices: [{ id: "go", label: "감시", role_by_vehicle: {} }] }, ui: {} },
    { id: "watch", name: "감시", do: { kind: "watch_target", params: { target: "nearest", distance_m: 150 } },
      on: [{ cond: { kind: "battery_below", params: { pct: 30 } }, go_step: "home" }], ui: {} },
    { id: "home", name: "귀환", do: { kind: "return_home", params: {} }, on: [], ui: {} },
  ],
};
const step = (p: Role, id: string) => p.steps.find((s) => s.id === id)!;

describe("updateStep", () => {
  it("changes one step and leaves the input role as it was", () => {
    const next = updateStep(role, "watch", (s) => ({ ...s, name: "근접 감시" }));
    expect(step(next, "watch").name).toBe("근접 감시");
    expect(step(role, "watch").name).toBe("감시");
  });
});

describe("setActionKind", () => {
  it("keeps the target and distance between target actions", () => {
    expect(step(setActionKind(role, "watch", "approach_target"), "watch").do).toEqual(
      { kind: "approach_target", params: { target: "nearest", distance_m: 150 } });
  });
  it("gives a target action the nearest target and a distance when it had none", () => {
    expect(step(setActionKind(role, "home", "watch_target"), "home").do.params).toEqual({ target: "nearest", distance_m: 150 });
  });
  it("strikes the same target without a distance", () => {
    expect(step(setActionKind(role, "watch", "strike_target"), "watch").do.params).toEqual({ target: "nearest" });
  });
  it("moves to a point taken from the role's route (coordinates are not typed in)", () => {
    expect(step(setActionKind(role, "home", "move_to"), "home").do.params).toEqual({ target: { lat: 37.9, lon: 124.6 } });
  });
  it("makes a one-point route from a move target", () => {
    const moved = setActionKind(role, "home", "move_to");
    expect(step(setActionKind(moved, "home", "patrol_route"), "home").do.params).toEqual({ route: [{ lat: 37.9, lon: 124.6 }] });
  });
  it("falls back to the given point (the zone centre) when the role has no point yet", () => {
    const blank: Role = { ...role, steps: [{ id: "start", name: "시작", do: { kind: "hold", params: {} }, on: [], ui: {} }], entry: "start" };
    const centre = { lat: 37.96, lon: 124.67 };
    expect(step(setActionKind(blank, "start", "move_to", centre), "start").do.params).toEqual({ target: centre });
    expect(step(setActionKind(blank, "start", "patrol_route", centre), "start").do.params).toEqual({ route: [centre] });
  });
  it("prefers the role's own point over the fallback", () => {
    expect(step(setActionKind(role, "home", "move_to", { lat: 0, lon: 0 }), "home").do.params).toEqual({ target: { lat: 37.9, lon: 124.6 } });
  });
  it("clears the params for hold and return home", () => {
    expect(step(setActionKind(role, "watch", "hold"), "watch").do).toEqual({ kind: "hold", params: {} });
  });
});

describe("defaultCondition", () => {
  it("starts the battery threshold at 30 %", () => {
    expect(defaultCondition("battery_below", step(role, "watch"))).toEqual({ kind: "battery_below", params: { pct: 30 } });
  });
  it("points an operator choice at the step's first report choice", () => {
    expect(defaultCondition("operator_choice", step(role, "report"))).toEqual({ kind: "operator_choice", params: { choice: "go" } });
  });
});

describe("addStepAfter", () => {
  it("puts a hold card right after the step and links to it on arrival", () => {
    const { role: next, id } = addStepAfter(role, "patrol");
    expect(next.steps.map((s) => s.id)).toEqual(["patrol", id, "report", "watch", "home"]);
    expect(step(next, id)).toMatchObject({ name: "새 카드", do: { kind: "hold", params: {} }, on: [] });
    expect(step(next, "patrol").on.at(-1)).toEqual({ cond: { kind: "arrived", params: {} }, go_step: id });
  });
  it("never reuses an existing id", () => {
    const once = addStepAfter(role, "patrol");
    const twice = addStepAfter(once.role, "patrol");
    expect(twice.id).not.toBe(once.id);
  });
});

describe("removeStep", () => {
  it("drops the step, the exits into it and an emergency link to it", () => {
    const next = removeStep(role, "home");
    expect(next.steps.map((s) => s.id)).toEqual(["patrol", "report", "watch"]);
    expect(step(next, "watch").on).toEqual([]);
    expect(next.emergency.battery_low_step).toBeNull();
  });
  it("keeps the entry step", () => {
    expect(removeStep(role, "patrol")).toBe(role);
  });
});

describe("report choices", () => {
  it("adds a choice with a fresh id", () => {
    const choices = step(addChoice(role, "report"), "report").report!.choices;
    expect(choices.map((c) => c.id)).toEqual(["go", "c1"]);
    expect(choices[1]).toEqual({ id: "c1", label: "선택 2", role_by_vehicle: {} });
  });
  it("removes a choice and the exit that waited for it", () => {
    const s = step(removeChoice(role, "report", "go"), "report");
    expect(s.report!.choices).toEqual([]);
    expect(s.on).toEqual([]);
  });
});

describe("zoneCentre", () => {
  it("averages the zone's points", () => {
    expect(zoneCentre({ points: [{ lat: 0, lon: 0 }, { lat: 2, lon: 0 }, { lat: 2, lon: 4 }, { lat: 0, lon: 4 }] })).toEqual({ lat: 1, lon: 2 });
  });
});

const SQUARE: RouteDef = { id: "square_300", name: "사각형 수색 300m", points: [], offsets: [{ north_m: 300, east_m: 0 }] };
const NORTH: RouteDef = { id: "base_to_north", name: "기지 → 북쪽 해역", points: [{ lat: 37.97, lon: 124.7, alt_m: 0 }], offsets: [] };
const routeRole: Role = { id: "r", name: "r", domains: ["air"], entry: "a", approved: true, steps: [
  { id: "a", name: "a", do: { kind: "move_to", params: { target: { lat: 37.9, lon: 124.7, alt_m: 0 } } }, on: [] },
] };

describe("route flying", () => {
  it("copies a relative route into the card and keeps the kind", () => {
    const s = step(applyRoute(routeRole, "a", SQUARE), "a");
    expect(s.do).toEqual({ kind: "move_to", params: { offsets: SQUARE.offsets, route_name: "사각형 수색 300m" } });
  });
  it("copies a fixed route's points as the route", () => {
    expect(step(applyRoute(routeRole, "a", NORTH), "a").do.params).toEqual({ route: NORTH.points, route_name: "기지 → 북쪽 해역" });
  });
  it("turns looping on and off without touching the route", () => {
    const named = applyRoute(routeRole, "a", NORTH);
    const loop = step(setLoop(named, "a", true), "a").do;
    expect(loop).toEqual({ kind: "patrol_route", params: { route: NORTH.points, route_name: "기지 → 북쪽 해역" } });
    expect(step(setLoop(setLoop(named, "a", true), "a", false), "a").do.kind).toBe("move_to");
  });
  it("makes a one-point route when a point move starts looping", () => {
    expect(step(setLoop(routeRole, "a", true), "a").do.params).toEqual({ route: [{ lat: 37.9, lon: 124.7, alt_m: 0 }] });
  });
  it("drops route values when the card leaves route flying", () => {
    const p = applyRoute(routeRole, "a", SQUARE);
    expect(step(setActionKind(p, "a", "hold"), "a").do.params).toEqual({});
  });
  it("finds the listed route by name and keeps an unnamed route as the current value", () => {
    expect(routeChoice({ offsets: SQUARE.offsets, route_name: "사각형 수색 300m" }, [NORTH, SQUARE])).toBe("square_300");
    expect(routeChoice({ route: [NORTH.points![0], NORTH.points![0]] }, [NORTH, SQUARE])).toBe("");
  });
  it("defaults a T+ condition to one minute", () => {
    expect(defaultCondition("at_time", routeRole.steps[0])).toEqual({ kind: "at_time", params: { offset_ms: 60000 } });
  });
});

describe("cardOptions", () => {
  it("offers route controls and T+ on a friendly route card", () => {
    const o = cardOptions("move_to", false);
    expect(o.routeControls).toBe(true);
    expect(o.conditions).toContain("at_time");
  });
  it("keeps an enemy card's route as the script has it and offers no T+ (sim steers enemies by target or route only)", () => {
    const o = cardOptions("move_to", true);
    expect(o.routeControls).toBe(false);
    expect(o.conditions).not.toContain("at_time");
    expect(cardOptions("patrol_route", true).routeControls).toBe(false);
  });
  it("has no route controls on a card that is not route flying", () => {
    expect(cardOptions("hold", false).routeControls).toBe(false);
  });
});
