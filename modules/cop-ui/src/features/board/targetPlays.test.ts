import { describe, expect, it } from "vitest";
import type { ActionKind, Domain, Play } from "../../contracts.gen";
import { targetPlays } from "./targetPlays";

const play = (id: string, kind: ActionKind, domains: Domain[]): Play =>
  ({ id, name: id, domains, entry: "s", steps: [{ id: "s", name: "s", do: { kind } }] });
const PLAYS = [play("watch", "watch_target", ["air"]), play("track_fast", "watch_target", ["air"]),
  play("approach", "approach_target", ["sea"]), play("strike", "strike_target", ["air", "sea"]),
  play("patrol_a", "patrol_route", ["air"])];

describe("targetPlays", () => {
  it("offers the plays whose first step works a target and that the vehicle's domain runs, never strike", () => {
    expect(targetPlays(PLAYS, "air").map((p) => p.id)).toEqual(["watch", "track_fast"]);
    expect(targetPlays(PLAYS, "sea").map((p) => p.id)).toEqual(["approach"]);
    expect(targetPlays(PLAYS, "ground")).toEqual([]);
  });
});
