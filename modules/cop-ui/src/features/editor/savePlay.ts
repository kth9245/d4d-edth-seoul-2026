import type { Play, PlayCheck } from "../../contracts.gen";

type Fetch = (url: string, init?: RequestInit) => Promise<Response>;

// POST /plays: the server checks the play and saves it (resetting the run) only when ok.
export async function savePlay(play: Play, f: Fetch = (url, init) => fetch(url, init)): Promise<PlayCheck> {
  const r = await f("/plays", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(play),
  });
  if (!r.ok) throw new Error(`/plays answered ${r.status}: ${await r.text()}`);
  return (await r.json()) as PlayCheck;
}
