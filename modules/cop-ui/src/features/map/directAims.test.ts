import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import type { Frame, VehicleState } from "../../contracts.gen";
import { directAims } from "./directAims";

const base = s1 as Frame;
const north = { lat: 38.029, lon: 124.699 };
const alt = { lat: 37.9995, lon: 124.7044 };

function withD1(patch: Partial<VehicleState>): Frame {
  return { ...base, vehicles: base.vehicles.map((v) => (v.id === "d1" ? { ...v, ...patch } : v)) };
}
const directMove = (target: { lat: number; lon: number }) => ({
  command: { id: "cmd-d1", vehicle_id: "d1", kind: "move" as const, params: { target },
    provenance: { source: "operator_direct" as const, operator_id: "op1", issued_ms: base.t_ms } },
  checks: ["zone"], passed_ms: base.t_ms,
});

describe("directAims", () => {
  it("draws no cross when nobody is under direct control", () => {
    expect(directAims(base, null)).toEqual([]);
  });

  it("draws a cross where the server is taking a vehicle under direct control", () => {
    expect(directAims(withD1({ step_id: null, active: directMove(alt) }), null)).toEqual([{ label: "d1", ...alt }]);
  });

  it("drops the cross once the vehicle is back on its role step (arrived)", () => {
    expect(directAims(withD1({ step_id: "watch", active: directMove(alt) }), null)).toEqual([]);
  });

  it("shows the order just sent until a newer frame arrives", () => {
    const pending = { label: "d1", ...north, sentAt: base.t_ms };
    expect(directAims(base, pending)).toEqual([{ label: "d1", ...north }]);
  });

  it("forgets the sent order once a newer frame says otherwise (blocked: no cross)", () => {
    const pending = { label: "d1", ...north, sentAt: base.t_ms - 1000 };
    expect(directAims(base, pending)).toEqual([]);
  });

  it("lets the sent order replace the server's older cross for the same vehicle", () => {
    const pending = { label: "d1", ...north, sentAt: base.t_ms };
    expect(directAims(withD1({ step_id: null, active: directMove(alt) }), pending)).toEqual([{ label: "d1", ...north }]);
  });
});
