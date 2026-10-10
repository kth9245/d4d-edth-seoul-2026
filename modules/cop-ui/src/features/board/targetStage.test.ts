import { describe, expect, it } from "vitest";
import type { Frame, Target } from "../../contracts.gen";
import { at, mkFrame, mkReport, mkTarget, mkVehicle, T0 } from "./boardFixtures";
import { targetStage } from "./targetStage";
import { trackState } from "./trackState";

const LANDING = at(37.978, 124.7);
const stage = (f: Frame, t: Target) => targetStage(f, t, trackState(t, f.t_ms, LANDING));
const seen = mkTarget({ id: "boat1", seen_by: ["d1"], first_seen_ms: T0 - 1 });
const strikeCmd = { command: { id: "c", vehicle_id: "d2", kind: "strike" as const, params: {} }, checks: [], passed_ms: 0 };

describe("targetStage", () => {
  it("says struck, striking, then waiting for strike approval before anything else", () => {
    expect(stage(mkFrame(), { ...seen, neutralized_ms: T0 })).toMatchObject({ key: "gone", label: "무력화" });
    const striking = mkFrame({ vehicles: [mkVehicle({ id: "d2", status: "active", target_id: "boat1", active: strikeCmd })] });
    expect(stage(striking, seen)).toEqual({ key: "strike", label: "타격 중", detail: "d2", away: false });
    const asking = mkFrame({ reports: [mkReport({ id: "r", vehicle_id: "usv", target_id: "boat1", text: "타격 승인 요청 · usv",
      choices: [{ id: "x", label: "함께 타격" }] })] });
    expect(stage(asking, seen)).toEqual({ key: "ask", label: "허락 대기", detail: "usv 요청", away: false });
  });

  it("says lost with time and direction, red when it moves away", () => {
    const fast1 = mkTarget({ id: "fast1", first_seen_ms: T0 - 60_000, last_seen_ms: T0 - 20_000,
      last_seen_pos: at(37.987, 124.745), last_seen_vel_east_mps: 6.3 });
    expect(stage(mkFrame(), fast1)).toEqual({ key: "lost", label: "놓침", detail: "0:20 전 · 이탈(도주) 추정 6.3 m/s", away: true });
  });

  it("says RF only and never detected", () => {
    expect(stage(mkFrame(), mkTarget({ id: "b", rf_detected: true })).key).toBe("rf");
    // decision 0071: a heat or sound clue is not "radio only", the stage names what was picked up
    expect(stage(mkFrame(), mkTarget({ id: "b", rf_detected: true }))).toMatchObject({ label: "RF 탐지", detail: "무선만 잡힘" });
    expect(stage(mkFrame(), mkTarget({ id: "b", sound_detected: true }))).toMatchObject({ key: "rf", label: "소음 탐지", detail: "소음만 잡힘" });
    expect(stage(mkFrame(), mkTarget({ id: "b", rf_detected: true, ir_detected: true }))).toMatchObject({ label: "RF·열 탐지", detail: "RF·열만 잡힘" });
    expect(stage(mkFrame(), mkTarget({ id: "c" }))).toEqual({ key: "never", label: "미탐", detail: "센서에 안 잡힘", away: false });
  });

  it("says tracked only by vehicles on a mission, else found by who sees it", () => {
    const on = mkFrame({ vehicles: [mkVehicle({ id: "d1", status: "active", target_id: "boat1" })] });
    expect(stage(on, seen)).toEqual({ key: "track", label: "추적", detail: "d1", away: false });
    const home = mkFrame({ vehicles: [mkVehicle({ id: "d1", status: "maintenance", target_id: "boat1" })] });
    expect(stage(home, seen)).toEqual({ key: "found", label: "발견", detail: "d1 관측", away: false });
  });
});
