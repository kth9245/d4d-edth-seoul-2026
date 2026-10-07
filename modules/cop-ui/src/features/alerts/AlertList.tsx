import type { Frame } from "../../contracts.gen";

const LABEL: Record<string, string> = { observe: "관찰", soft_kill: "소프트킬", hard_kill: "하드킬" };

export function AlertList({ frame }: { frame: Frame | null }) {
  if (!frame) return <div className="alerts">연결 대기 중…</div>;
  const resp = new Map(frame.responses.map((r) => [r.track_id, r]));
  const rows = [...frame.assessments].sort((a, b) => b.threat - a.threat);
  return (
    <div className="alerts">
      <h2>위협 목록</h2>
      {rows.map((a) => {
        const kind = resp.get(a.track_id)?.kind ?? "observe";
        return (
          <div key={a.track_id} className={`alert ${kind}`}>
            <b>{a.track_id}</b> {a.object_class} · 위협 {a.threat.toFixed(2)} · {LABEL[kind]}
            <div className="reason">{a.reason}</div>
          </div>
        );
      })}
    </div>
  );
}
