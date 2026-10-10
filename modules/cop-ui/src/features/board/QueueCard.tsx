import type { Frame } from "../../contracts.gen";
import type { Card } from "../cards/frameCards";
import { postSettle } from "../cards/injectionRequests";
import { postDecision } from "../cards/postDecision";
import { postDirect } from "../cards/postDirect";
import type { Sent } from "../cards/postJson";
import { choiceGroups } from "./choiceGroups";
import type { QueueItem } from "./decisionQueue";

export type SendState = { state: "sending" } | { state: "sent"; id: string } | { state: "error"; error: string };
export type Send = (cardId: string, request: () => Promise<Sent>) => void;

const BLOCK_KO: Record<string, string> = { outside_zone: "작전 구역 밖", battery_insufficient: "귀환 배터리 부족", no_provenance: "근거 없음" };
const tone = (r: number) => (r >= 0.7 ? "hi" : r >= 0.4 ? "mid" : "lo");
const isApproval = (c: Card) => c.source === "report" && c.text.startsWith("타격 승인 요청");

function Note({ card, s, paused }: { card: Card; s?: SendState; paused: boolean }) {
  if (s?.state === "error") return <div className="note error">보내기 실패: {s.error}</div>;
  if (s?.state !== "sent") return null;
  return <div className="note">{card.source === "block" ? `대안 지점 보냄 ${s.id}` : `보냄 ${s.id} · ${paused ? "재생하면 반영" : "다음 틱에 반영"}`}</div>;
}

// One open queue item (Part1-32): title, sensor line, why it asks, risk with its reasons, the question, then the
// buttons — planned choices first and drone requests grouped (decision 0046), target picks as risk-ordered chips
// per vehicle, strike approval in red, approve / reject for a switch, the alternative point for a block.
export function QueueCard({ frame, item, sent, send, onGraph }: {
  frame: Frame; item: QueueItem; sent: Record<string, SendState>; send: Send; onGraph?: (target: string) => void;
}) {
  const c = item.cards[0];
  const paused = frame.run.status === "paused";
  const locked = (id: string) => sent[id]?.state === "sending" || sent[id]?.state === "sent";
  const battery = (v: string) => frame.vehicles.find((x) => x.id === v)?.battery_pct;
  const head = (title: string, tid: string | null) => (
    <div className="head"><b>{title}</b>{tid && <span className="tid">{tid}</span>}<time>{c.time}</time></div>
  );

  if (c.source === "block") return (
    <div className="card first t-block">
      {head(`명령 차단 · ${BLOCK_KO[c.kind] ?? c.kind}`, c.vehicle)}
      <div className="text">{c.text}</div>
      <div className="hint">{c.vehicle}는 하던 일을 계속합니다. 안전 검사가 고른 대안 지점으로 보낼 수 있습니다.</div>
      <div className="q">대안 지점으로 보낼까요?</div>
      {c.alternative && c.vehicle && (
        <button className="wide go" disabled={locked(c.id)} onClick={() => send(c.id, () => postDirect(c.vehicle!, c.alternative!))}>
          대안 지점으로<small>{c.vehicle} → {c.alternative.lat.toFixed(4)}, {c.alternative.lon.toFixed(4)}</small>
        </button>
      )}
      <Note card={c} s={sent[c.id]} paused={paused} />
    </div>
  );

  if (c.source === "injection") return (
    <div className="card first">
      {head(`전환 승인 · ${c.text}`, c.vehicle)}
      <div className="text">{c.preview}</div>
      <div className="settle">
        <button className="wide pri" disabled={locked(c.id)} onClick={() => send(c.id, () => postSettle(c.id, true))}>승인</button>
        <button className="wide" disabled={locked(c.id)} onClick={() => send(c.id, () => postSettle(c.id, false))}>거부</button>
      </div>
      <Note card={c} s={sent[c.id]} paused={paused} />
    </div>
  );

  if (c.kind === "target_select") {
    const vs = item.cards.map((x) => x.vehicle).join("·");
    return (
      <div className="card first">
        {head("추적할 표적 선택", vs)}
        <div className="hint">위험도가 가장 높은 표적이 맨 앞입니다. 기체마다 하나씩 고릅니다.</div>
        {item.cards.map((x) => {
          const opts = x.choices.map((ch) => ({ ch, t: frame.targets.find((t) => t.id === ch.label.split(" ")[0]) }))
            .sort((a, b) => (b.t?.threat ?? 0) - (a.t?.threat ?? 0));
          return (
            <div key={x.id} className="selrow">
              <span className="who">{x.vehicle}<small>{Math.round(battery(x.vehicle ?? "") ?? 0)}%</small></span>
              <div className="tchips">
                {opts.map(({ ch, t }, i) => {
                  const r = (t?.threat ?? 0) / 100;
                  return (
                    <button key={ch.id} className={`tchip ${tone(r)}${i === 0 ? " top" : ""}`} disabled={locked(x.id)}
                      onClick={() => send(x.id, () => postDecision(x.id, ch.id))}>
                      {t?.id ?? ch.label}<em>{r.toFixed(2)}{t?.rf_detected ? " RF" : ""}</em>
                    </button>
                  );
                })}
              </div>
              <Note card={x} s={sent[x.id]} paused={paused} />
            </div>
          );
        })}
      </div>
    );
  }

  const ap = isApproval(c);
  const { planned, requests } = choiceGroups(c.choices);
  const sensor = c.text.split(" · ").slice(1).join(" · ") || c.text;
  const hint = ap ? "사람이 고르기 전에는 어떤 기체도 타격하지 않습니다."
    : `${c.vehicle}는 그 배 위에 머뭅니다. 정해진 대응을 고르거나, 기지 대기 드론에게 비는 해안이나 함께 감시를 맡기세요.`;
  return (
    <div className={`card first${ap ? " t-danger" : ""}`}>
      {head(ap ? "타격 허락 요청" : "표적 발견", c.target ?? null)}
      <div className="text">{sensor}</div>
      <div className="hint">{hint}</div>
      {c.threat && (
        <div className={`threat${c.threat.rf ? " rf" : ""}`}>
          <span className={`sc ${tone(c.threat.score)}`}>위험 {c.threat.score.toFixed(2)}</span>
          {c.threat.parts.slice(1).map((p) => <span key={p} className="why">{p}</span>)}
        </div>
      )}
      <div className="q">{ap ? "타격을 허락할까요?" : "누구를 보낼까요?"}</div>
      {planned.map((ch, i) => (
        <button key={ch.id} className={`wide ${ap ? (i === 0 ? "strike" : "strike2") : ch.preview ? "pri" : ""}`}
          disabled={locked(c.id)} onClick={() => send(c.id, () => postDecision(c.id, ch.id))}>
          {ch.label}<small>{ch.preview || "아무 기체도 옮기지 않음"}</small>
        </button>
      ))}
      {requests.length > 0 && <div className="reqs">기지 대기 드론에게 맡기기</div>}
      {requests.map((g) => (
        <div key={g.what} className="grp">
          <span className="gl">{g.what}</span>
          <span className="vs">
            {g.options.map((o) => {
              const b = battery(o.vehicle);
              return (
                <button key={o.choiceId} className={`vbtn${b !== undefined && b < 50 ? " low" : ""}`} disabled={locked(c.id)}
                  onClick={() => send(c.id, () => postDecision(c.id, o.choiceId))}>
                  {o.vehicle}<small>{b !== undefined ? `${Math.round(b)}%` : ""}</small>
                </button>
              );
            })}
          </span>
        </div>
      ))}
      <Note card={c} s={sent[c.id]} paused={paused} />
      {onGraph && c.target && <button className="graph-open" onClick={() => onGraph(c.target!)}>연결 보기</button>}
    </div>
  );
}
