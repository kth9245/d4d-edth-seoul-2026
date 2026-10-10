import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import s4 from "../../../../../contracts/examples/frames/s4_switch_pending.json";
import s6 from "../../../../../contracts/examples/frames/s6_battery_block.json";
import s7 from "../../../../../contracts/examples/frames/s7_strike_approval.json";
import s8 from "../../../../../contracts/examples/frames/s8_neutralized.json";
import type { Frame } from "../../contracts.gen";
import { frameCards } from "./frameCards";

describe("frameCards", () => {
  it("makes an open report card with its choices and what each choice switches", () => {
    const [c] = frameCards(s1 as Frame);
    expect(c).toMatchObject({ id: "rep-d1-1791634270000", source: "report", kind: "target_detected",
      vehicle: "d1", time: "21:11:10", text: "미식별 선박 접근", done: null, target: "boat1" });
    expect(c.choices).toEqual([{ id: "approach", label: "근접 확인",
      preview: "d1→watch · usv→approach · ugv→landing" }]); // d2 already patrols (decision 0036)
  });

  it("shows a pending injection from Frame.injections instead of its injection_pending report", () => {
    const cards = frameCards(s4 as Frame);
    expect(cards.filter((c) => c.kind === "injection_pending")).toEqual([]);
    const inj = cards.find((c) => c.source === "injection")!;
    expect(inj).toMatchObject({ id: "inj-1", vehicle: "d2·usv", text: "고속 보트 추적", done: null, choices: [],
      preview: "d2→track_fast · usv→track_fast_sea" });
  });

  it("shows each block from Frame.blocks with its reason and detail, not the command_blocked reports", () => {
    const cards = frameCards(s6 as Frame);
    expect(cards.filter((c) => c.kind === "command_blocked")).toEqual([]);
    const blocks = cards.filter((c) => c.source === "block");
    expect(blocks.map((b) => [b.id, b.kind, b.text])).toEqual([
      ["cmd-d2-1791634830000", "battery_insufficient", "필요 2210s > 가용 1490s · 대안 지점 있음"],
      ["cmd-d2-1791634800000", "outside_zone", "작전 구역 밖(38.0500, 124.6600) · 대안 지점 있음"],
    ]);
  });

  it("carries the alternative point a block offers, for the same vehicle", () => {
    const battery = frameCards(s6 as Frame).find((c) => c.id === "cmd-d2-1791634830000")!;
    expect(battery.alternative).toEqual({ lat: 37.9196, lon: 124.7652 });
    const noAlt = { ...(s6 as Frame), blocks: [{ ...(s6 as Frame).blocks[0], alternative: null }] };
    expect(frameCards(noAlt).find((c) => c.source === "block")!.alternative).toBeNull();
  });

  it("puts the newest card first among cards that wait for nobody", () => {
    const rest = frameCards(s6 as Frame).filter((c) => c.choices.length === 0);
    const times = rest.map((c) => c.t_ms);
    expect(times).toEqual([...times].sort((a, b) => b - a));
  });

  // Decision 0040: the contact card shows the observed risk of its target (Target.threat and threat_reasons,
  // filled by sensing) and the open cards are ordered by that risk, so a boat that starts emitting jumps up.
  const f1 = s1 as Frame;
  const boat = (id: string, threat: number, reasons: string[]) =>
    ({ ...f1.targets[0], id, threat, threat_reasons: reasons, vel_east_mps: 3, vel_north_mps: -4 });
  const contact = (id: string, target: string, t_ms: number) => ({ ...f1.reports[0], id, target_id: target, t_ms });

  it("adds the observed risk of the card's target as one line", () => {
    const f = { ...f1, targets: [boat("boat1", 58, ["kind_boat", "inside_watch_radius", "speed"])] };
    expect(frameCards(f)[0].threat).toMatchObject({
      score: 0.58, rf: false, line: "관측 위험 0.58 · 스캔 판별: 보트 · 기준점 반경 안 +0.30 · 속도 5.0 m/s" });
  });

  // Decisions 0041/0043: outside the watch radius but within three times it adds +0.15, so the line adds up.
  it("says the boat is near the watch point when it is outside the radius but within three times it", () => {
    const f = { ...f1, targets: [boat("boat1", 72, ["kind_boat", "near_watch_radius", "rf_emission", "speed"])] };
    expect(frameCards(f)[0].threat?.line).toBe(
      "관측 위험 0.72 · 스캔 판별: 보트 · 기준점 근접 +0.15 · RF 방출 감지 +0.30 · 속도 5.0 m/s");
  });

  it("adds the heat and noise clues to the score line (decision 0071)", () => {
    const f = { ...f1, targets: [boat("boat1", 55, ["kind_unknown", "near_watch_radius", "ir_signature", "sound"])] };
    expect(frameCards(f)[0].threat?.line).toBe(
      "관측 위험 0.55 · 스캔 전: 미상 · 기준점 근접 +0.15 · 열 신호 감지 +0.10 · 소음 감지 +0.10");
  });

  it("says RF when our vehicles picked up its emission and 'before scan' when nobody has seen its kind", () => {
    const f = { ...f1, targets: [boat("boat1", 60, ["kind_unknown", "rf_emission"])] };
    expect(frameCards(f)[0].threat).toMatchObject({ score: 0.6, rf: true, line: "관측 위험 0.60 · 스캔 전: 미상 · RF 방출 감지 +0.30" });
  });

  it("keeps each risk reason as its own item for the board (Part1-32)", () => {
    const f = { ...f1, targets: [boat("boat1", 75, ["kind_boat", "rf_emission"])] };
    const [c] = frameCards(f);
    expect(c.threat?.parts).toEqual(["관측 위험 0.75", "스캔 판별: 보트", "RF 방출 감지 +0.30"]);
    expect(c.threat?.line).toBe(c.threat?.parts.join(" · "));
  });

  it("has no risk line before sensing scored the target", () => {
    expect(frameCards(f1)[0].threat).toBeUndefined();
  });

  it("puts the open cards first, riskiest on top, even above newer events", () => {
    const f = { ...f1,
      targets: [boat("boat1", 50, ["kind_boat"]), boat("boat2", 80, ["kind_boat", "rf_emission"])],
      reports: [contact("rep-a", "boat1", 1000), contact("rep-b", "boat2", 900),
        { ...f1.reports[0], id: "gap", kind: "vehicle_gap" as const, choices: [], t_ms: 2000 }] };
    expect(frameCards(f).map((c) => c.id)).toEqual(["rep-b", "rep-a", "gap"]);
  });

  it("marks resolved reports and settled injections done, with no choices", () => {
    const cards = frameCards(s7 as Frame);
    const detected = cards.find((c) => c.id === "rep-d1-1791634270000")!;
    expect(detected).toMatchObject({ done: "처리됨 21:11:30", choices: [] });
    expect(cards.find((c) => c.id === "inj-1")!.done).toBe("승인됨");
  });

  it("says on the result card which operator decision and checks the strike went through", () => {
    const hit = frameCards(s8 as Frame).find((c) => c.kind === "target_neutralized")!;
    expect(hit).toMatchObject({ vehicle: "d2", text: "fast1 무력화(d2)", choices: [], done: null,
      preview: "운용자 결정 dec-4 '함께 타격' → d2·usv 타격 · 출처·구역·배터리 검사 통과" });
  });
});
