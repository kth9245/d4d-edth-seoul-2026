import type { Queue } from "./decisionQueue";
import type { Stage, StageKey } from "./targetStage";

export interface Situation { targets: number; stages: { key: StageKey; label: string; n: number }[]; decisions: number }

const URGENT: [StageKey, string][] = [["ask", "허락 대기"], ["strike", "타격 중"], ["lost", "놓침"], ["rf", "RF 탐지"],
  ["track", "추적"], ["found", "발견"], ["gone", "무력화"], ["never", "미탐"]];

// Header line (Part1-32): targets per stage, most urgent first (counts, not an order of events), and the
// decisions waiting. A merged target pick holds one decision per vehicle.
export function situationCounts(stages: Stage[], queue: Queue): Situation {
  return {
    targets: stages.length,
    stages: URGENT.map(([key, label]) => ({ key, label, n: stages.filter((x) => x.key === key).length })).filter((x) => x.n > 0),
    decisions: queue.action.reduce((n, item) => n + item.cards.length, 0),
  };
}

// Header count of enemies (decision 0080): no counter word, since "척" counts only ships and the enemies can be
// sites, ground robots or drones.
export function targetsLabel(n: number): string {
  return `적 ${n}`;
}
