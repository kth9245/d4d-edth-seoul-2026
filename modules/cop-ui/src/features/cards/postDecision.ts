import type { Accepted, DecisionIn } from "../../contracts.gen";

export type Sent = { ok: true; id: string } | { ok: false; error: string };

// One click on a report choice → POST /decisions (contracts/API.md §5). Never throws: the card shows the error.
export async function postDecision(report_id: string, choice_id: string): Promise<Sent> {
  const body: DecisionIn = { report_id, choice_id };
  let r: Response;
  try {
    r = await fetch("/decisions", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  } catch {
    return { ok: false, error: "서버 연결 실패" };
  }
  const data = await r.json().catch(() => null);
  if (r.ok && data) return { ok: true, id: (data as Accepted).id };
  const detail = typeof data?.detail === "string" ? ` ${data.detail}` : "";
  return { ok: false, error: `${r.status}${detail}` };
}
