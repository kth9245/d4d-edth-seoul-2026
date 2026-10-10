import { describe, expect, it } from "vitest";
import demo from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { CapabilityReason, Ontology, OntologyView, Operation, Play, VehicleSpec } from "../../contracts.gen";
import { kindRows, reasonLine, reserveLines } from "./ontologyView";

const onto = demo.ontology as unknown as Ontology;
const vehicles = demo.vehicles as unknown as VehicleSpec[];
const why = (r: Partial<CapabilityReason>) => ({ via: null, ...r }) as CapabilityReason;

describe("kindRows", () => {
  it("lists each parent before its children with depth, what it adds and its vehicles", () => {
    const rows = kindRows(onto, vehicles);
    expect(rows.map((r) => [r.id, r.depth])).toEqual([["vehicle", 0], ["air_vehicle", 1], ["recon_drone", 2],
      ["armed_drone", 2], ["sea_vehicle", 1], ["armed_usv", 2], ["ground_vehicle", 1], ["ground_robot", 2]]);
    expect(rows[1].adds).toBe("감시·접근·통신 중계");
    expect(rows[2].vehicles).toEqual(expect.arrayContaining(["d1", "d3"]));
    expect(rows[3].vehicles).toEqual(["d2"]);
    expect(rows[6].adds).toBe("watch_point");
  });
});

describe("reasonLine", () => {
  it("names the kinds walked and the group that gave the action", () => {
    expect(reasonLine(why({ action: "watch_target", allowed: true, path: ["recon_drone", "air_vehicle"], via: "watch" }), onto))
      .toBe("정찰 드론 → 공중 기체 (감시 묶음)");
  });
  it("says nothing up to the root gave it", () => {
    expect(reasonLine(why({ action: "strike_target", allowed: false, path: ["recon_drone", "air_vehicle", "vehicle"] }), onto))
      .toBe("정찰 드론 → 공중 기체 → 기체, 어디에도 없음");
  });
  it("shows a single action given without its group", () => {
    expect(reasonLine(why({ action: "watch_point", allowed: true, path: ["ground_robot", "ground_vehicle"], via: "watch_point" }), onto))
      .toBe("지상 로봇 → 지상 기체 (watch_point)");
  });
});

describe("reserveLines", () => {
  const op = { assign: { d1: "patrol_a" }, reserve: { d1: ["d3"] }, switches: [] } as unknown as Operation;
  const plays = [{ id: "patrol_a", steps: [{ do: { kind: "hold" } }, { do: { kind: "patrol_route" } }] }] as unknown as Play[];
  const view = (allowed: string[]) => ({ ontology: onto, vehicles: [{ vehicle_id: "d3", kind: "recon_drone",
    reasons: allowed.map((a) => why({ action: a as CapabilityReason["action"], allowed: true, path: [] })) }] }) as OntologyView;
  it("says the reserve can run every action of the plays it may take over", () => {
    expect(reserveLines(op, plays, view(["hold", "patrol_route"]), vehicles))
      .toEqual(["d3는 d1의 예비. d1의 플레이가 쓰는 행동 2개를 d3가 모두 할 수 있음(같은 정찰 드론)"]);
  });
  it("names what the reserve cannot do", () => {
    expect(reserveLines(op, plays, view(["hold"]), vehicles))
      .toEqual(["d3는 d1의 예비. d1의 플레이가 쓰는 행동 중 patrol_route를 d3가 못 함"]);
  });
});
