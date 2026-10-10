import type { Operation } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /operation: the running operation becomes this one and the run goes back to its start, paused.
export async function postOperation(op: Operation, f: Fetch = (url, init) => fetch(url, init)): Promise<Operation> {
  const r = await f("/operation", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(op) });
  if (!r.ok) throw new Error(`/operation answered ${r.status}`);
  return (await r.json()) as Operation;
}
