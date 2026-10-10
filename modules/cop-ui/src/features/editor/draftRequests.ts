import type { DraftIn, Role } from "../../contracts.gen";

export type Drafted = { ok: true; role: Role } | { ok: false; error: string };

// Sentence → POST /roles/draft → AI draft role (origin ai_draft, approved false). A cache miss may take minutes.
export async function postDraft(text: string): Promise<Drafted> {
  const body: DraftIn = { text };
  try {
    const r = await fetch("/roles/draft", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) return { ok: false, error: `응답 ${r.status}` };
    return { ok: true, role: (await r.json()) as Role };
  } catch {
    return { ok: false, error: "서버 응답 없음" };
  }
}

// Saving is the operator's approval of an AI draft (decision 0003): the server stores it only when the check
// passes, and safety blocks every command of a role that is not approved.
export function forSave(role: Role): Role {
  return role.origin === "ai_draft" && !role.approved ? { ...role, approved: true } : role;
}
