import { describe, expect, it } from "vitest";
import type { VehicleSpec } from "../../contracts.gen";
import { at, mkFrame, mkReport, mkVehicle } from "./boardFixtures";
import { vehicleRows } from "./vehicleRows";

const spec = (id: string, kind: string): VehicleSpec =>
  ({ id, name: id, domain: "air", speed_mps: 15, endurance_min: 100, sensor_range_m: 800, home: at(37.95, 124.7), kind });
const NAMES = { patrol_a: "해안 순찰 A", strike: "표적 타격" };
const strikeCmd = { command: { id: "c", vehicle_id: "d2", kind: "strike" as const, params: {} }, checks: [], passed_ms: 0 };

describe("vehicleRows", () => {
  it("says what each vehicle does, its kind, battery and whether a card waits for it", () => {
    const f = mkFrame({
      vehicles: [mkVehicle({ id: "d1", status: "active", role_id: "patrol_a", target_id: "boat1", battery_pct: 82.6 }),
        mkVehicle({ id: "d3" })],
      reports: [mkReport({ id: "r", vehicle_id: "d1", choices: [{ id: "c", label: "근접 확인" }] })],
    });
    expect(vehicleRows(f, NAMES, [spec("d1", "recon_drone")])).toEqual([
      { id: "d1", status: "active", doing: "해안 순찰 A", kind: "정찰 드론", target: "boat1", striking: false, battery: 83, low: false, waiting: true },
      { id: "d3", status: "ready", doing: "대기", kind: "", target: null, striking: false, battery: 100, low: false, waiting: false },
    ]);
  });

  it("shows no target for a vehicle back at base, and marks a striking one and low battery", () => {
    const f = mkFrame({ vehicles: [
      mkVehicle({ id: "d1", status: "maintenance", role_id: "go_home", target_id: "boat1", battery_pct: 20 }),
      mkVehicle({ id: "d2", status: "active", role_id: "strike", target_id: "fast1", active: strikeCmd, battery_pct: 29 }),
      mkVehicle({ id: "d4", status: "returning", role_id: "go_home" }),
    ] });
    const rows = vehicleRows(f, NAMES, []);
    expect(rows.map((r) => [r.doing, r.target, r.striking, r.low])).toEqual([
      ["기지 정비", null, false, true], ["표적 타격", "fast1", true, true], ["귀환 중", null, false, false],
    ]);
  });
});
