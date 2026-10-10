import type { Metrics } from "../../contracts.gen";
import { metricView } from "./metricView";
import "./run.css";

// Side column: operator actions next to the manual baseline counted in the same run (docs/research/09 2.3).
export function MetricsPanel({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) return null;
  const v = metricView(metrics);
  return (
    <section className="metrics">
      <div className="pair">
        <div className="operator"><b>{v.operator}</b><span>운용자 조작</span></div>
        <div className="manual"><b>{v.manual}</b><span>기체별 직접 명령이었다면</span></div>
      </div>
      <dl>
        {v.rows.map(([k, val]) => (
          <div key={k}><dt>{k}</dt><dd>{val}</dd></div>
        ))}
      </dl>
      <p className="note">수동 기준 = 같은 실행에서 엔진이 만든 명령 수 + 보고 카드 수. 사람이 실제로 누른 수가 아닙니다.</p>
    </section>
  );
}
