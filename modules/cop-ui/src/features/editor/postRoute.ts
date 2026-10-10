import type { RouteDef } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /routes (decision 0054): the route joins the running operation's list; returns the whole list.
export async function postRoute(route: RouteDef, f: Fetch = (url, init) => fetch(url, init)): Promise<RouteDef[]> {
  const r = await f("/routes", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(route) });
  if (!r.ok) throw new Error(`/routes answered ${r.status}`);
  return (await r.json()) as RouteDef[];
}
