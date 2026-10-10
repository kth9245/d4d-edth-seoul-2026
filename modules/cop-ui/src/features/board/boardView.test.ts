import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import type { Block, Frame } from "../../contracts.gen";
import { mkFrame, mkVehicle, T0 } from "./boardFixtures";
import { boardView } from "./boardView";
import { NO_BOARD_DATA } from "./fetchBoardData";

describe("boardView", () => {
  it("draws the board from a Frame even before plays, specs and watch points arrive", () => {
    const v = boardView(s1 as Frame, NO_BOARD_DATA);
    expect(Object.keys(v.tracks)).toEqual(["boat1"]);
    expect(v.stages.boat1.key).toBe("found"); // d1 sees boat1 but has no target_id in this example
    expect(v.queue.action.map((i) => i.key)).toEqual(["rep-d1-1791634270000"]);
    expect(v.situation.decisions).toBe(1);
    expect(v.rows.map((r) => r.id)).toEqual(["d1", "d2", "d3", "usv", "ugv", "d4"]);
  });

  it("drops a block from the queue once its vehicle got a command issued after it (review of Task 2)", () => {
    const block: Block = { command_id: "cmd-1", vehicle_id: "d2", reason: "outside_zone", detail: "작전 구역 밖", t_ms: T0,
      alternative: { id: "cmd-1-alt", vehicle_id: "d2", kind: "move", params: { target: { lat: 38, lon: 124.6 } } } };
    const moved = (issued: number) => mkVehicle({ id: "d2", status: "active", active: { checks: [], passed_ms: issued,
      command: { id: "c", vehicle_id: "d2", kind: "move", provenance: { source: "operator_direct", issued_ms: issued } } } });
    const waiting = boardView(mkFrame({ t_ms: T0 + 2_000, blocks: [block], vehicles: [moved(T0 - 9_000)] }), NO_BOARD_DATA);
    expect(waiting.queue.action.map((i) => i.key)).toEqual(["cmd-1"]);
    const sent = boardView(mkFrame({ t_ms: T0 + 2_000, blocks: [block], vehicles: [moved(T0 + 1_000)] }), NO_BOARD_DATA);
    expect([sent.queue.action, sent.queue.alerts.map((c) => c.id)]).toEqual([[], ["cmd-1"]]);
  });
});
