import { useEffect, useRef, useState } from "react";
import type { Frame } from "../../contracts.gen";
import type { Card } from "../cards/frameCards";
import { pruneSent } from "../cards/pruneSent";
import type { Queue, QueueItem } from "./decisionQueue";
import { QueueCard, type Send, type SendState } from "./QueueCard";

const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");

function Row({ item, onOpen }: { item: QueueItem; onOpen: () => void }) {
  const c = item.cards[0];
  const ap = c.source === "report" && c.text.startsWith("타격 승인 요청");
  const [b, who] = c.source === "block" ? [c.vehicle, "명령 차단 · 대안 지점"]
    : c.source === "injection" ? [c.text, "전환 승인"]
    : c.kind === "target_select" ? [item.cards.map((x) => x.vehicle).join("·"), "쫓을 표적 고르기"]
    : [c.target, ap ? `${c.vehicle} 타격 허락 요청` : `${c.vehicle} 발견 · 누구를 보낼지`];
  return (
    <button type="button" className={`qrow${ap || c.source === "block" ? " t-danger" : ""}`} onClick={onOpen}>
      <b>{b}</b>{c.threat && <span className={`sc ${tone(c.threat.score)}`}>{c.threat.score.toFixed(2)}</span>}
      <span className="who">{who}</span><time>{c.time}</time><span className="go">▸</span>
    </button>
  );
}

// The strike result stays as the answer to "what now" after its alert ages out (review of Task 6: at ×10 a
// 2-minute alert lasts 12 s, and the strike is the last scene).
function Idle({ frame, seen, onGraph }: { frame: Frame; seen: Card[]; onGraph?: (target: string) => void }) {
  const win = seen.find((c) => c.kind === "target_neutralized");
  const m = frame.metrics;
  return win ? (
    <div className="next-act done"><div className="k">작전 결과</div><div className="t">{win.target} 무력화 — 사람 허락 뒤 타격</div>
      <div className="s">운용자 조작 {m.operator_actions ?? 0}번 (기체별 직접 명령이었다면 {m.manual_baseline_actions ?? 0}번)</div>
      {win.preview && <div className="s why">{win.preview}</div>}
      {onGraph && win.target && <button className="graph-open" onClick={() => onGraph(win.target!)}>연결 보기</button>}</div>
  ) : (
    <div className="next-act"><div className="k">할 일 없음</div><div className="t">지금 결정할 것이 없습니다</div>
      <div className="s">▶ 재생하거나 다음 사건으로 넘어가세요.</div></div>
  );
}

// Right column (Part1-32): the decision queue — one item open (the first, or the one the operator opened), the
// rest one line each; with nothing waiting, what to do next. One answer per card, locked while sending and after
// the server accepted it until the Frame shows it done; a reset forgets what was sent (UI-20).
export function DecisionQueue({ frame, queue, onGraph }: { frame: Frame; queue: Queue; onGraph?: (target: string) => void }) {
  const [sent, setSent] = useState<Record<string, SendState>>({});
  const [openKey, setOpenKey] = useState<string | null>(null);
  const lastT = useRef(0);
  useEffect(() => {
    const back = frame.t_ms < lastT.current;
    lastT.current = frame.t_ms;
    const ids = [...frame.reports.map((r) => r.id), ...frame.injections.map((i) => i.id), ...frame.blocks.map((b) => b.command_id)];
    setSent((m) => pruneSent(m, ids, back));
  }, [frame]);
  const send: Send = async (cardId, request) => {
    const s = sent[cardId]?.state;
    if (s === "sending" || s === "sent") return;
    setSent((m) => ({ ...m, [cardId]: { state: "sending" } }));
    const r = await request();
    setSent((m) => ({ ...m, [cardId]: r.ok ? { state: "sent", id: r.id } : { state: "error", error: r.error } }));
  };
  // A merged target pick changes key when one of its picks is answered; keep it open by the cards it still holds.
  const opened = (openKey ?? "").split("+");
  const open = queue.action.find((i) => i.key === openKey || i.cards.some((c) => opened.includes(c.id))) ?? queue.action[0];
  const decisions = queue.action.reduce((n, i) => n + i.cards.length, 0);
  return (
    <div className="queue">
      {open ? (
        <>
          <div className="sec">결정 대기 <b>{decisions}</b><span className="ord">타격 허락 · 차단 · 위험도 순</span></div>
          {queue.action.map((item) => (item === open
            ? <QueueCard key={item.key} frame={frame} item={item} sent={sent} send={send} onGraph={onGraph} />
            : <Row key={item.key} item={item} onOpen={() => setOpenKey(item.key)} />))}
        </>
      ) : <Idle frame={frame} seen={[...queue.alerts, ...queue.history]} onGraph={onGraph} />}
      {queue.alerts.length > 0 && <div className="sec">알림</div>}
      {queue.alerts.map((c) => (
        <div key={`${c.source}-${c.id}`} className={`alert${c.kind === "target_neutralized" ? " win" : c.source === "block" ? " blk" : ""}`}>
          <b>{c.kind === "target_neutralized" ? `${c.target} 무력화` : c.text}</b><time>{c.time}</time>
          {c.preview && <span className="why">{c.preview}</span>}
          {onGraph && c.target && c.kind === "target_neutralized" && <button className="graph-open" onClick={() => onGraph(c.target!)}>연결 보기</button>}
        </div>
      ))}
    </div>
  );
}
