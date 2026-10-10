import { describe, expect, it } from "vitest";
import s1 from "../../../../../contracts/examples/frames/s1_report_wait.json";
import s4 from "../../../../../contracts/examples/frames/s4_switch_pending.json";
import s6 from "../../../../../contracts/examples/frames/s6_battery_block.json";
import type { Frame } from "../../contracts.gen";
import { frameCards } from "./frameCards";

describe("frameCards", () => {
  it("makes an open report card with its choices and what each choice switches", () => {
    const [c] = frameCards(s1 as Frame);
    expect(c).toMatchObject({ id: "rep-d1-1791634270000", source: "report", kind: "target_detected",
      vehicle: "d1", time: "21:11:10", text: "미식별 선박 접근", done: null });
    expect(c.choices).toEqual([{ id: "approach", label: "근접 확인",
      preview: "d1→watch · usv→approach · ugv→landing · d2→patrol_b" }]);
  });

  it("shows a pending injection from Frame.injections instead of its injection_pending report", () => {
    const cards = frameCards(s4 as Frame);
    expect(cards.filter((c) => c.kind === "injection_pending")).toEqual([]);
    const inj = cards.find((c) => c.source === "injection")!;
    expect(inj).toMatchObject({ id: "inj-1", vehicle: "d2", text: "고속 보트 추적: d2", done: null, choices: [],
      preview: "d2→track_fast" });
  });

  it("shows each block from Frame.blocks with its reason and detail, not the command_blocked reports", () => {
    const cards = frameCards(s6 as Frame);
    expect(cards.filter((c) => c.kind === "command_blocked")).toEqual([]);
    const blocks = cards.filter((c) => c.source === "block");
    expect(blocks.map((b) => [b.id, b.kind, b.text])).toEqual([
      ["cmd-d2-1791635490000", "battery_insufficient", "필요 1873s > 가용 960s · 대안 지점 있음"],
      ["cmd-d2-1791635460000", "outside_zone", "작전 구역 밖(38.0500, 124.7000) · 대안 지점 있음"],
    ]);
  });

  it("puts the newest card first", () => {
    const times = frameCards(s6 as Frame).map((c) => c.t_ms);
    expect(times).toEqual([...times].sort((a, b) => b - a));
  });

  it("marks resolved reports and settled injections done, with no choices", () => {
    const cards = frameCards(s6 as Frame);
    const detected = cards.find((c) => c.id === "rep-d1-1791634270000")!;
    expect(detected).toMatchObject({ done: "처리됨 21:11:30", choices: [] });
    expect(cards.find((c) => c.id === "inj-1")!.done).toBe("승인됨");
  });
});
