import type { DraftIn, Play } from "../../contracts.gen";

export type Drafted = { ok: true; play: Play } | { ok: false; error: string };

// Sentence → POST /plays/draft → AI draft play (origin ai_draft, approved false). A cache miss may take minutes.
export async function postDraft(text: string): Promise<Drafted> {
  const body: DraftIn = { text };
  try {
    const r = await fetch("/plays/draft", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) return { ok: false, error: `응답 ${r.status}` };
    return { ok: true, play: (await r.json()) as Play };
  } catch {
    return { ok: false, error: "서버 응답 없음" };
  }
}

// Saving is the operator's approval of an AI draft (decision 0003): the server stores it only when the check
// passes, and safety blocks every command of a play that is not approved.
export function forSave(play: Play): Play {
  return play.origin === "ai_draft" && !play.approved ? { ...play, approved: true } : play;
}
