type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// DELETE /plays/{id} (decision 0050): the server drops the play from the running operation and resets the run.
// true = the server had it; false = 404, a new play that was only on screen (never saved). Other failures throw.
export async function deletePlay(id: string, f: Fetch = (url, init) => fetch(url, init)): Promise<boolean> {
  const url = `/plays/${encodeURIComponent(id)}`;
  const r = await f(url, { method: "DELETE" });
  if (r.status === 404) return false;
  if (!r.ok) throw new Error(`${url} answered ${r.status}`);
  return true;
}
