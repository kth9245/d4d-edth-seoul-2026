import { describe, expect, it } from "vitest";
import { mkCard, T0 } from "./boardFixtures";
import { decisionQueue } from "./decisionQueue";

const ask = { id: "c", label: "근접 확인", preview: "" };
const ids = (q: ReturnType<typeof decisionQueue>) => q.action.map((i) => i.cards.map((c) => c.id).join("+"));

describe("decisionQueue", () => {
  it("puts open reports with choices and pending switches in the queue, answered ones in history", () => {
    const q = decisionQueue([
      mkCard({ id: "open", choices: [ask] }),
      mkCard({ id: "answered", done: "처리됨 21:00:05" }),
      mkCard({ id: "inj-1", source: "injection", kind: "injection" }),
      mkCard({ id: "inj-2", source: "injection", kind: "injection", done: "승인됨" }),
    ], T0);
    expect(ids(q)).toEqual(["inj-1", "open"]);
    expect(q.history.map((c) => c.id)).toEqual(["answered", "inj-2"]);
  });

  it("asks about a block with an alternative for 30 s, then shows it as an alert for 2 min, then history", () => {
    const block = mkCard({ id: "cmd-1", source: "block", kind: "outside_zone", alternative: { lat: 38, lon: 124.6 } });
    expect(ids(decisionQueue([block], T0 + 29_000))).toEqual(["cmd-1"]);
    expect(decisionQueue([block], T0 + 31_000).alerts.map((c) => c.id)).toEqual(["cmd-1"]);
    expect(decisionQueue([block], T0 + 121_000).history.map((c) => c.id)).toEqual(["cmd-1"]);
  });

  it("orders strike approval, block, switch, then risk, newest first on a tie", () => {
    const risk = (s: number) => ({ score: s, rf: false, line: "", parts: [] });
    const q = decisionQueue([
      mkCard({ id: "low", choices: [ask], threat: risk(0.42) }),
      mkCard({ id: "high", choices: [ask], threat: risk(0.75) }),
      mkCard({ id: "inj", source: "injection", kind: "injection" }),
      mkCard({ id: "blk", source: "block", kind: "battery_insufficient", alternative: { lat: 37.9, lon: 124.7 } }),
      mkCard({ id: "strike", choices: [ask], text: "타격 승인 요청 · usv 센서 탐지", threat: risk(0.1) }),
      mkCard({ id: "high-new", choices: [ask], threat: risk(0.75), t_ms: T0 + 1 }),
    ], T0 + 1);
    expect(ids(q)).toEqual(["strike", "blk", "inj", "high-new", "high", "low"]);
  });

  it("merges the target picks one switch opened into one item, one decision per vehicle", () => {
    const pick = (id: string, vehicle: string) => mkCard({ id, kind: "target_select", vehicle, choices: [ask] });
    const q = decisionQueue([pick("p-d2", "d2"), pick("p-usv", "usv")], T0);
    expect(ids(q)).toEqual(["p-d2+p-usv"]);
    expect(decisionQueue([pick("p-d2", "d2")], T0).action[0].key).toBe("p-d2");
  });

  it("keeps a fresh strike result as an alert and older events in history, newest first", () => {
    const q = decisionQueue([
      mkCard({ id: "old", kind: "target_neutralized", t_ms: T0 - 200_000 }),
      mkCard({ id: "win", kind: "target_neutralized", t_ms: T0 - 5_000 }),
      mkCard({ id: "older", done: "처리됨", t_ms: T0 - 300_000 }),
    ], T0);
    expect(q.alerts.map((c) => c.id)).toEqual(["win"]);
    expect(q.history.map((c) => c.id)).toEqual(["old", "older"]);
  });
});
