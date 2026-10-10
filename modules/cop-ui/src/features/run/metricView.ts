import type { Metrics } from "../../contracts.gen";
import { mmss } from "./mmss";

export type MetricView = { operator: number; manual: number; rows: [string, string][] };

// Frame.metrics for the panel (definitions: docs/research/09 2.3). Fields are optional in TS, so missing = 0.
export function metricView(m: Metrics): MetricView {
  const mission = m.mission_success == null ? "판정 전" : m.mission_success ? "성공" : "실패";
  return {
    operator: m.operator_actions ?? 0,
    manual: m.manual_baseline_actions ?? 0,
    rows: [
      ["결정", String(m.decisions ?? 0)],
      ["보낸 명령", String(m.commands_sent ?? 0)],
      ["차단된 명령", String(m.blocked_commands ?? 0)],
      ["기체 공백", mmss(m.vehicle_gap_ms ?? 0)],
      ["동시 미결 카드 최대", String(m.open_reports_max ?? 0)],
      ["임무", mission],
    ],
  };
}
