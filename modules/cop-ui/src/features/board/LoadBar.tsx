import type { Metrics } from "../../contracts.gen";
import { metricView } from "../run/metricView";

// Header, right (Part1-32): operator actions next to the manual baseline of the same run (docs/research/09 2.3).
// The other numbers and what the baseline means sit in the tooltip.
export function LoadBar({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) return null;
  const v = metricView(metrics);
  const title = [...v.rows.map(([k, x]) => `${k} ${x}`),
    "수동 기준 = 같은 실행에서 엔진이 만든 명령 수 + 보고 카드 수(사람이 누른 수가 아님)"].join("\n");
  return (
    <div className="loadbar" title={title}>
      <span className="op"><b>{v.operator}</b><small>운용자<br />조작</small></span>
      <span className="vs">vs</span>
      <span className="man"><b>{v.manual}</b><small>기체별 직접<br />명령이었다면</small></span>
    </div>
  );
}
