import type { DecisionIn } from "../../contracts.gen";
import { postJson, type Sent } from "./postJson";

export type { Sent };

// One click on a report choice → POST /decisions (contracts/API.md §5).
export function postDecision(report_id: string, choice_id: string): Promise<Sent> {
  const body: DecisionIn = { report_id, choice_id };
  return postJson("/decisions", body);
}
