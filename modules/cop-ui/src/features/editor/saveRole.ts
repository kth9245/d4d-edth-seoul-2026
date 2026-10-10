import type { Role, RoleCheck } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /roles: the server checks the role and saves it (resetting the run) only when ok.
export async function saveRole(role: Role, f: Fetch = (url, init) => fetch(url, init)): Promise<RoleCheck> {
  const r = await f("/roles", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(role),
  });
  if (!r.ok) throw new Error(`/roles answered ${r.status}: ${await r.text()}`);
  return (await r.json()) as RoleCheck;
}
