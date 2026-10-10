import { useEffect, useRef, useState } from "react";
import type { Frame } from "../../contracts.gen";
import "./cards.css";
import { type Card, frameCards } from "./frameCards";
import { postDecision } from "./postDecision";
import { pruneSent } from "./pruneSent";

const TITLE: Record<Card["kind"], string> = {
  target_detected: "표적 발견", target_select: "표적 선택", vehicle_gap: "감시 공백", vehicle_lost: "기체 상실",
  battery_low: "배터리 부족", injection_pending: "전환 승인 대기", command_blocked: "명령 차단",
  injection: "전환 승인 대기", outside_zone: "차단 · 구역 밖", battery_insufficient: "차단 · 배터리 부족",
  no_provenance: "차단 · 근거 없음",
};
const TONE: Partial<Record<Card["kind"], string>> = {
  vehicle_gap: "warn", vehicle_lost: "warn", battery_low: "warn", injection: "pending",
  outside_zone: "block", battery_insufficient: "block", no_provenance: "block",
};

type SendState = { state: "sending" } | { state: "sent"; id: string } | { state: "error"; error: string };

// Side column: one card per report / injection / block, newest first; choice buttons → POST /decisions.
export function CardList({ frame }: { frame: Frame | null }) {
  const [sent, setSent] = useState<Record<string, SendState>>({});
  const lastT = useRef(0);
  useEffect(() => {
    if (!frame) return;
    const back = frame.t_ms < lastT.current;
    lastT.current = frame.t_ms;
    setSent((m) => pruneSent(m, frame.reports.map((r) => r.id), back));
  }, [frame]);
  if (!frame) return null;
  const cards = frameCards(frame);
  const paused = frame.run.status === "paused";

  const choose = async (reportId: string, choiceId: string) => {
    const s = sent[reportId]?.state;
    if (s === "sending" || s === "sent") return; // one decision per report
    setSent((m) => ({ ...m, [reportId]: { state: "sending" } }));
    const r = await postDecision(reportId, choiceId);
    setSent((m) => ({ ...m, [reportId]: r.ok ? { state: "sent", id: r.id } : { state: "error", error: r.error } }));
  };

  if (cards.length === 0) return <div className="cards empty">아직 보고 없음</div>;
  return (
    <div className="cards">
      {cards.map((c) => {
        const s = sent[c.id];
        const locked = s?.state === "sending" || s?.state === "sent";
        return (
          <div key={`${c.source}-${c.id}`} className={`card ${TONE[c.kind] ?? "info"}${c.done ? " done" : ""}`}>
            <div className="head">
              <b>{TITLE[c.kind]}</b>
              {c.vehicle && <span>{c.vehicle}</span>}
              <time>{c.time}</time>
            </div>
            <div className="text">{c.text}</div>
            {c.choices.map((ch) => (
              <button key={ch.id} disabled={locked} onClick={() => choose(c.id, ch.id)}>
                {ch.label}
                {ch.preview && <small>{ch.preview}</small>}
              </button>
            ))}
            {!c.done && s?.state === "sent" && (
              <div className="note">보냄 {s.id} · {paused ? "재생하면 반영" : "다음 틱에 반영"}</div>
            )}
            {!c.done && s?.state === "error" && <div className="note error">보내기 실패: {s.error}</div>}
            {c.done && <div className="note">{c.done}</div>}
          </div>
        );
      })}
    </div>
  );
}
