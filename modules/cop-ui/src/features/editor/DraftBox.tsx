import { useState } from "react";
import sentences from "../../../../../demo/draft_sentences.json";
import type { Play } from "../../contracts.gen";
import { postDraft } from "./draftRequests";

// Top of the editor sidebar (Part3-13): a sentence → POST /plays/draft → the AI draft opens as an unsaved play.
// The example buttons fill the demo sentences exactly, since the cache only matches the same sentence; any
// other sentence goes to the LLM (tens of seconds or more) or, offline, falls back to the standby template.
export function DraftBox({ onDrafted }: { onDrafted: (play: Play) => void }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<{ ok: boolean; text: string } | null>(null);

  const make = async () => {
    setBusy(true);
    setNote(null);
    const t0 = performance.now();
    const r = await postDraft(text.trim());
    setBusy(false);
    if (!r.ok) return setNote({ ok: false, text: `초안 실패: ${r.error}` });
    onDrafted(r.play);
    const sec = ((performance.now() - t0) / 1000).toFixed(1);
    setNote(r.play.origin === "ai_draft"
      ? { ok: true, text: `AI 초안 도착 ${sec}s · 저장 전에 검토` }
      : { ok: false, text: "AI 응답 없음 · 대기 템플릿으로 대체" });
  };

  return (
    <section className="draftbox">
      <textarea aria-label="AI 초안 문장" rows={3} value={text} placeholder="임무를 문장으로 적으면 AI가 플레이 초안을 만듭니다"
        onChange={(e) => setText(e.target.value)} />
      <div className="examples">
        {sentences.map((s) => (
          <button key={s.id} title={s.text} onClick={() => setText(s.text)}>예시 · {s.text.slice(0, 12)}…</button>
        ))}
      </div>
      <button className="draft" disabled={busy || !text.trim()} onClick={make}>{busy ? "AI 초안 만드는 중…" : "초안 만들기"}</button>
      {note && <div className={note.ok ? "note" : "note warn"}>{note.text}</div>}
    </section>
  );
}
