import { useState } from "react";
import type { ActionKind, Choice, ConditionKind, Exit, GeoPoint, Polygon, Role, RouteDef, Step } from "../../contracts.gen";
import { ACTION_LABEL, CONDITION_LABEL, describeAction } from "./describe";
import { RouteMaker } from "./RouteMaker";
import { addChoice, applyRoute, cardOptions, defaultCondition, EDIT_ACTIONS, removeChoice, ROUTE_KINDS, routeChoice, setActionKind, setLoop,
  updateStep } from "./editStep";

const NEW_ROUTE = "__new_route__"; // the route select's "＋ 경로 추가" entry (decision 0054)

type Props = {
  role: Role;
  step: Step;
  vehicleIds: string[];
  roles: { id: string; name: string }[];
  fallbackPoint?: GeoPoint | null; // where a new move or route starts when the role has no point (zone centre)
  routes?: RouteDef[]; // decision 0044: what the route select offers
  enemy?: boolean; // an enemy role keeps its script: no route select, no T+ (decision 0045)
  onChange: (next: Role) => void;
  onAddAfter: () => void;
  onRemove: () => void;
  onClose: () => void;
  zone?: Polygon | null; // decision 0054: the route window's map
  onAddRoute?: (route: RouteDef) => Promise<void>;
};

const TARGET_LABEL: Record<string, string> = { nearest: "가장 가까운 표적", operator: "운용자가 고름" };
const num = (v: string) => (v.trim() === "" || Number.isNaN(Number(v)) ? null : Number(v));
// A kind the editor does not offer (does nothing in this simulator) stays selectable on the card that has it.
const withCurrent = <T extends string>(list: T[], cur: T) => (list.includes(cur) ? list : [...list, cur]);

// Side panel for the card picked on the graph (Part3-12.1). Every change goes up as a new role; saving and the
// server check stay as they are.
export function StepEditor({ role, step, vehicleIds, roles, fallbackPoint = null, routes = [], enemy = false, onChange, onAddAfter, onRemove, onClose,
  zone = null, onAddRoute }: Props) {
  const [makingRoute, setMakingRoute] = useState(false); // decision 0054
  const set = (change: (s: Step) => Step) => onChange(updateStep(role, step.id, change));
  const params = step.do.params ?? {};
  const setParam = (k: string, v: unknown) => set((s) => ({ ...s, do: { ...s.do, params: { ...(s.do.params ?? {}), [k]: v } } }));
  const exits = step.on ?? [];
  const setExits = (on: Exit[]) => set((s) => ({ ...s, on }));
  const others = role.steps.filter((s) => s.id !== step.id);
  const choices = step.report?.choices ?? [];
  const setChoice = (id: string, change: (c: Choice) => Choice) =>
    set((s) => ({ ...s, report: s.report && { ...s.report, choices: (s.report.choices ?? []).map((c) => (c.id === id ? change(c) : c)) } }));
  const targeted = ["watch_target", "approach_target", "strike_target"].includes(step.do.kind);
  // Decision 0045: move_to and patrol_route are one action here, "경로 비행"; 반복 picks which.
  const isRoute = ROUTE_KINDS.includes(step.do.kind);
  const options = cardOptions(step.do.kind, enemy);
  const nonRoute = EDIT_ACTIONS.filter((k) => !ROUTE_KINDS.includes(k));
  const current = routeChoice(params, routes);
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
        <select aria-label="행동" value={isRoute ? "route" : step.do.kind}
          onChange={(e) => onChange(setActionKind(role, step.id, (e.target.value === "route" ? "patrol_route" : e.target.value) as ActionKind, fallbackPoint))}>
          <option value="route">경로 비행</option>
          {(isRoute ? nonRoute : withCurrent(nonRoute, step.do.kind)).map((k) => <option key={k} value={k}>{ACTION_LABEL[k] ?? k}</option>)}
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
        {options.routeControls && (
          <div className="se-route">
            <label className="se-check">
              <input type="checkbox" aria-label="반복" checked={step.do.kind === "patrol_route"}
                onChange={(e) => onChange(setLoop(role, step.id, e.target.checked))} /> 반복
            </label>
            <select aria-label="경로" value={current}
              onChange={(e) => {
                if (e.target.value === NEW_ROUTE) return setMakingRoute(true);
                const r = routes.find((x) => x.id === e.target.value);
                if (r) onChange(applyRoute(role, step.id, r));
              }}>
              {current === "" && <option value="">지금 값 유지: {describeAction(step.do)}</option>}
              <optgroup label="고정 경로">
                {routes.filter((r) => !r.offsets?.length).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
              </optgroup>
              <optgroup label="상대 경로 (기체 위치 기준)">
                {routes.filter((r) => r.offsets?.length).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
              </optgroup>
              {zone && onAddRoute && <option value={NEW_ROUTE}>＋ 경로 추가</option>}
            </select>
            {makingRoute && zone && onAddRoute && (
              <RouteMaker zone={zone} existingIds={routes.map((r) => r.id)} onCancel={() => setMakingRoute(false)}
                onSave={(r) => onAddRoute(r).then(() => {
                  onChange(applyRoute(role, step.id, r));
                  setMakingRoute(false);
                })} />
            )}
          </div>
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
                {withCurrent(options.conditions, ex.cond.kind).map((k) => <option key={k} value={k}>{CONDITION_LABEL[k] ?? k}</option>)}
              </select>
              {ex.cond.kind === "battery_below" && (
                <label className="se-num">
                  <input aria-label={`연결 ${i + 1} 배터리`} type="number" min={0} max={100} value={Number(ex.cond.params?.pct ?? 30)}
                    onChange={(e) => num(e.target.value) !== null && put({ ...ex, cond: { ...ex.cond, params: { pct: num(e.target.value)! } } })} /> % 미만
                </label>
              )}
              {ex.cond.kind === "at_time" && (() => {
                const ms = Number(ex.cond.params?.offset_ms ?? 0);
                const setMs = (m: number, sec: number) => put({ ...ex, cond: { ...ex.cond, params: { offset_ms: (m * 60 + sec) * 1000 } } });
                return (
                  <span className="se-num">T+
                    <input aria-label={`연결 ${i + 1} 분`} type="number" min={0} value={Math.floor(ms / 60000)}
                      onChange={(e) => num(e.target.value) !== null && setMs(num(e.target.value)!, Math.floor(ms / 1000) % 60)} />분
                    <input aria-label={`연결 ${i + 1} 초`} type="number" min={0} max={59} value={Math.floor(ms / 1000) % 60}
                      onChange={(e) => num(e.target.value) !== null && setMs(Math.floor(ms / 60000), num(e.target.value)!)} />초
                  </span>
                );
              })()}
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
                  <button className="se-x" aria-label={`선택지 ${ci + 1} 지우기`} onClick={() => onChange(removeChoice(role, step.id, c.id))}>✕</button>
                </div>
                {Object.entries(c.role_by_vehicle ?? {}).map(([v, pid]) => {
                  const pbv = (next: Record<string, string>) => setChoice(c.id, (x) => ({ ...x, role_by_vehicle: next }));
                  const rest = Object.fromEntries(Object.entries(c.role_by_vehicle ?? {}).filter(([k]) => k !== v));
                  return (
                    <div key={v} className="se-row se-pbv">
                      <select aria-label={`선택지 ${ci + 1} 기체 ${v}`} value={v} onChange={(e) => pbv({ ...rest, [e.target.value]: pid })}>
                        {vehicleIds.filter((id) => id === v || !(id in (c.role_by_vehicle ?? {}))).map((id) => <option key={id} value={id}>{id}</option>)}
                      </select>
                      <span className="se-arrow">→</span>
                      <select aria-label={`선택지 ${ci + 1} ${v} Role`} value={pid} onChange={(e) => pbv({ ...rest, [v]: e.target.value })}>
                        {!roles.some((p) => p.id === pid) && <option value={pid}>{pid} (없음)</option>}
                        {roles.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                      </select>
                      <button className="se-x" aria-label={`선택지 ${ci + 1} ${v} 지우기`} onClick={() => pbv(rest)}>✕</button>
                    </div>
                  );
                })}
                {vehicleIds.some((id) => !(id in (c.role_by_vehicle ?? {}))) && roles.length > 0 && (
                  <button className="se-add" onClick={() => {
                    const v = vehicleIds.find((id) => !(id in (c.role_by_vehicle ?? {})))!;
                    setChoice(c.id, (x) => ({ ...x, role_by_vehicle: { ...(x.role_by_vehicle ?? {}), [v]: roles[0].id } }));
                  }}>+ 기체를 다른 Role로</button>
                )}
              </div>
            ))}
            <div className="se-row">
              <button className="se-add" onClick={() => onChange(addChoice(role, step.id))}>+ 선택지 추가</button>
              <button className="se-add" onClick={() => {
                const cleared = choices.reduce((p, c) => removeChoice(p, step.id, c.id), role);
                onChange(updateStep(cleared, step.id, (s) => ({ ...s, report: null })));
              }}>보고 없애기</button>
            </div>
          </>
        )}
      </div>

      <div className="se-sec se-cards">
        <button className="se-add" onClick={onAddAfter}>+ 뒤에 카드 추가</button>
        <button className="se-remove" onClick={onRemove} disabled={step.id === role.entry}
          title={step.id === role.entry ? "시작 카드는 지울 수 없습니다" : undefined}>카드 삭제</button>
      </div>
    </aside>
  );
}
