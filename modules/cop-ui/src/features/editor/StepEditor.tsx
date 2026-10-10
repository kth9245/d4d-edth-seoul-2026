import type { ActionKind, Choice, ConditionKind, Exit, GeoPoint, Play, Step } from "../../contracts.gen";
import { ACTION_LABEL, CONDITION_LABEL, describeAction } from "./describe";
import { addChoice, defaultCondition, EDIT_ACTIONS, EDIT_CONDITIONS, removeChoice, setActionKind, updateStep } from "./editStep";

type Props = {
  play: Play;
  step: Step;
  vehicleIds: string[];
  plays: { id: string; name: string }[];
  fallbackPoint?: GeoPoint | null; // where a new move or route starts when the play has no point (zone centre)
  onChange: (next: Play) => void;
  onAddAfter: () => void;
  onRemove: () => void;
  onClose: () => void;
};

const TARGET_LABEL: Record<string, string> = { nearest: "가장 가까운 표적", operator: "운용자가 고름" };
const num = (v: string) => (v.trim() === "" || Number.isNaN(Number(v)) ? null : Number(v));
// A kind the editor does not offer (does nothing in this simulator) stays selectable on the card that has it.
const withCurrent = <T extends string>(list: T[], cur: T) => (list.includes(cur) ? list : [...list, cur]);

// Side panel for the card picked on the graph (Part3-12.1). Every change goes up as a new play; saving and the
// server check stay as they are.
export function StepEditor({ play, step, vehicleIds, plays, fallbackPoint = null, onChange, onAddAfter, onRemove, onClose }: Props) {
  const set = (change: (s: Step) => Step) => onChange(updateStep(play, step.id, change));
  const params = step.do.params ?? {};
  const setParam = (k: string, v: unknown) => set((s) => ({ ...s, do: { ...s.do, params: { ...(s.do.params ?? {}), [k]: v } } }));
  const exits = step.on ?? [];
  const setExits = (on: Exit[]) => set((s) => ({ ...s, on }));
  const others = play.steps.filter((s) => s.id !== step.id);
  const choices = step.report?.choices ?? [];
  const setChoice = (id: string, change: (c: Choice) => Choice) =>
    set((s) => ({ ...s, report: s.report && { ...s.report, choices: (s.report.choices ?? []).map((c) => (c.id === id ? change(c) : c)) } }));
  const targeted = ["watch_target", "approach_target", "strike_target"].includes(step.do.kind);
  const target = typeof params.target === "string" ? params.target : "nearest";

  return (
    <aside className="step-editor nodrag" aria-label="카드 편집">
      <div className="se-head">
        <b>카드 편집</b> <code>{step.id}</code>
        <button className="se-close" onClick={onClose} aria-label="편집 닫기">✕</button>
      </div>

      <label className="se-field">이름
        <input aria-label="카드 이름" value={step.name} onChange={(e) => set((s) => ({ ...s, name: e.target.value }))} />
      </label>

      <div className="se-sec">
        <div className="se-title">행동</div>
        <select aria-label="행동" value={step.do.kind} onChange={(e) => onChange(setActionKind(play, step.id, e.target.value as ActionKind, fallbackPoint))}>
          {withCurrent(EDIT_ACTIONS, step.do.kind).map((k) => <option key={k} value={k}>{ACTION_LABEL[k] ?? k}</option>)}
        </select>
        {targeted && (
          <div className="se-row">
            <select aria-label="대상" value={target} onChange={(e) => setParam("target", e.target.value)}>
              {withCurrent(["nearest", "operator"], target).map((t) => <option key={t} value={t}>{TARGET_LABEL[t] ?? t}</option>)}
            </select>
            {step.do.kind !== "strike_target" && (
              <label className="se-num">거리
                <input aria-label="거리" type="number" min={0} value={typeof params.distance_m === "number" ? params.distance_m : ""}
                  onChange={(e) => num(e.target.value) !== null && setParam("distance_m", num(e.target.value))} /> m
              </label>
            )}
          </div>
        )}
        {(step.do.kind === "move_to" || step.do.kind === "patrol_route") && (
          <div className="se-note">{describeAction(step.do)} · 좌표는 그대로 둡니다(지도 편집 없음)</div>
        )}
      </div>

      <div className="se-sec">
        <div className="se-title">연결</div>
        {exits.map((ex, i) => {
          const put = (next: Exit) => setExits(exits.map((x, j) => (j === i ? next : x)));
          return (
            <div key={i} className="se-exit">
              <select aria-label={`연결 ${i + 1} 조건`} value={ex.cond.kind}
                onChange={(e) => put({ ...ex, cond: defaultCondition(e.target.value as ConditionKind, step) })}>
                {withCurrent(EDIT_CONDITIONS, ex.cond.kind).map((k) => <option key={k} value={k}>{CONDITION_LABEL[k] ?? k}</option>)}
              </select>
              {ex.cond.kind === "battery_below" && (
                <label className="se-num">
                  <input aria-label={`연결 ${i + 1} 배터리`} type="number" min={0} max={100} value={Number(ex.cond.params?.pct ?? 30)}
                    onChange={(e) => num(e.target.value) !== null && put({ ...ex, cond: { ...ex.cond, params: { pct: num(e.target.value)! } } })} /> % 미만
                </label>
              )}
              {ex.cond.kind === "operator_choice" && (
                <select aria-label={`연결 ${i + 1} 선택지`} value={String(ex.cond.params?.choice ?? "")}
                  onChange={(e) => put({ ...ex, cond: { ...ex.cond, params: { choice: e.target.value } } })}>
                  {choices.length === 0 && <option value="">보고 선택지 없음</option>}
                  {choices.map((c) => <option key={c.id} value={c.id}>'{c.label}' 선택 시</option>)}
                </select>
              )}
              <span className="se-arrow">→</span>
              <select aria-label={`연결 ${i + 1} 다음 카드`} value={ex.go_step} onChange={(e) => put({ ...ex, go_step: e.target.value })}>
                {!others.some((s) => s.id === ex.go_step) && <option value={ex.go_step}>{ex.go_step} (없음)</option>}
                {others.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
              <button className="se-x" aria-label={`연결 ${i + 1} 지우기`} onClick={() => setExits(exits.filter((_, j) => j !== i))}>✕</button>
            </div>
          );
        })}
        {others.length > 0 && (
          <button className="se-add" onClick={() => setExits([...exits, { cond: defaultCondition("target_found", step), go_step: others[0].id }])}>
            + 연결 추가
          </button>
        )}
      </div>

      <div className="se-sec">
        <div className="se-title">보고</div>
        {!step.report ? (
          <button className="se-add" onClick={() => set((s) => ({ ...s, report: { text: "", choices: [] } }))}>+ 보고 추가</button>
        ) : (
          <>
            <textarea aria-label="보고 문구" rows={2} value={step.report.text}
              onChange={(e) => set((s) => ({ ...s, report: s.report && { ...s.report, text: e.target.value } }))} />
            {choices.map((c, ci) => (
              <div key={c.id} className="se-choice">
                <div className="se-row">
                  <input aria-label={`선택지 ${ci + 1} 이름`} value={c.label} onChange={(e) => setChoice(c.id, (x) => ({ ...x, label: e.target.value }))} />
                  <button className="se-x" aria-label={`선택지 ${ci + 1} 지우기`} onClick={() => onChange(removeChoice(play, step.id, c.id))}>✕</button>
                </div>
                {Object.entries(c.play_by_vehicle ?? {}).map(([v, pid]) => {
                  const pbv = (next: Record<string, string>) => setChoice(c.id, (x) => ({ ...x, play_by_vehicle: next }));
                  const rest = Object.fromEntries(Object.entries(c.play_by_vehicle ?? {}).filter(([k]) => k !== v));
                  return (
                    <div key={v} className="se-row se-pbv">
                      <select aria-label={`선택지 ${ci + 1} 기체 ${v}`} value={v} onChange={(e) => pbv({ ...rest, [e.target.value]: pid })}>
                        {vehicleIds.filter((id) => id === v || !(id in (c.play_by_vehicle ?? {}))).map((id) => <option key={id} value={id}>{id}</option>)}
                      </select>
                      <span className="se-arrow">→</span>
                      <select aria-label={`선택지 ${ci + 1} ${v} 플레이`} value={pid} onChange={(e) => pbv({ ...rest, [v]: e.target.value })}>
                        {!plays.some((p) => p.id === pid) && <option value={pid}>{pid} (없음)</option>}
                        {plays.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                      </select>
                      <button className="se-x" aria-label={`선택지 ${ci + 1} ${v} 지우기`} onClick={() => pbv(rest)}>✕</button>
                    </div>
                  );
                })}
                {vehicleIds.some((id) => !(id in (c.play_by_vehicle ?? {}))) && plays.length > 0 && (
                  <button className="se-add" onClick={() => {
                    const v = vehicleIds.find((id) => !(id in (c.play_by_vehicle ?? {})))!;
                    setChoice(c.id, (x) => ({ ...x, play_by_vehicle: { ...(x.play_by_vehicle ?? {}), [v]: plays[0].id } }));
                  }}>+ 기체를 다른 플레이로</button>
                )}
              </div>
            ))}
            <div className="se-row">
              <button className="se-add" onClick={() => onChange(addChoice(play, step.id))}>+ 선택지 추가</button>
              <button className="se-add" onClick={() => {
                const cleared = choices.reduce((p, c) => removeChoice(p, step.id, c.id), play);
                onChange(updateStep(cleared, step.id, (s) => ({ ...s, report: null })));
              }}>보고 없애기</button>
            </div>
          </>
        )}
      </div>

      <div className="se-sec se-cards">
        <button className="se-add" onClick={onAddAfter}>+ 뒤에 카드 추가</button>
        <button className="se-remove" onClick={onRemove} disabled={step.id === play.entry}
          title={step.id === play.entry ? "시작 카드는 지울 수 없습니다" : undefined}>카드 삭제</button>
      </div>
    </aside>
  );
}
