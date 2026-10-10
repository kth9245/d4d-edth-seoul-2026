type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// DELETE /roles/{id} (decision 0050): the server drops the role from the running operation and resets the run.
// true = the server had it; false = 404, a new role that was only on screen (never saved). Other failures throw.
export async function deleteRole(id: string, f: Fetch = (url, init) => fetch(url, init)): Promise<boolean> {
  const url = `/roles/${encodeURIComponent(id)}`;
  const r = await f(url, { method: "DELETE" });
  if (r.status === 404) return false;
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return true;
}
