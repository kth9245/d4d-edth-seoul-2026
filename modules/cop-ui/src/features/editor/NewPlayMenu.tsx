import { useState } from "react";
import type { Domain, Play } from "../../contracts.gen";
import { blankPlay } from "./blankPlay";
import { DOMAIN_LABEL } from "./describe";
import { DraftBox } from "./DraftBox";

type Mode = "ai" | "manual" | null;

// Top of the editor sidebar (Part3-13.1): one "새로 만들기" button; it opens a choice between an AI draft
// (sentence → POST /plays/draft) and a play written by hand (one start card). Either one opens unsaved.
// The AI box stays open after a draft so its note (time, or "대기 템플릿으로 대체") stays readable.
export function NewPlayMenu({ existingIds, onCreated }: { existingIds: string[]; onCreated: (play: Play) => void }) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<Mode>(null);
  const [name, setName] = useState("");
  const [domain, setDomain] = useState<Domain>("air");
  const close = () => {
    setOpen(false);
    setMode(null);
    setName("");
  };

  return (
    <section className="newplay">
      <button className={open ? "newplay-toggle on" : "newplay-toggle"} aria-expanded={open}
        onClick={() => (open ? close() : setOpen(true))}>
        {open ? "× 닫기" : "＋ 새로 만들기"}
      </button>
      {open && mode === null && (
        <div className="newplay-pick">
          <button onClick={() => setMode("ai")}><b>AI로 생성</b><small>임무 문장 → 플레이 초안</small></button>
          <button onClick={() => setMode("manual")}><b>직접 생성</b><small>시작 카드 하나에서 시작</small></button>
        </div>
      )}
      {open && mode === "ai" && <DraftBox onDrafted={onCreated} />}
      {open && mode === "manual" && (
        <div className="newplay-manual">
          <input aria-label="플레이 이름" placeholder="플레이 이름" value={name} onChange={(e) => setName(e.target.value)} />
          <select aria-label="영역" value={domain} onChange={(e) => setDomain(e.target.value as Domain)}>
            {(Object.keys(DOMAIN_LABEL) as Domain[]).map((d) => <option key={d} value={d}>{DOMAIN_LABEL[d]}</option>)}
          </select>
          <button className="make" onClick={() => {
            onCreated(blankPlay(name, domain, existingIds));
            close();
          }}>만들기</button>
        </div>
      )}
      {open && mode !== null && <button className="newplay-back" onClick={() => setMode(null)}>← 다른 방법</button>}
    </section>
  );
}
