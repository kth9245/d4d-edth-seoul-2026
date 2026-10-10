import type { Action, ActionKind, Condition, ConditionKind, Domain } from "../../contracts.gen";

export const ACTION_LABEL: Record<ActionKind, string> = {
  move_to: "이동",
  patrol_route: "순찰 경로",
  search_area: "구역 수색",
  return_home: "귀환",
  watch_target: "표적 감시",
  watch_point: "지점 감시",
  approach_target: "표적 접근",
  relay_comms: "통신 중계",
  hold: "대기",
};

const CONDITION_LABEL: Record<ConditionKind, string> = {
  target_found: "표적 발견",
  arrived: "도착",
  time_elapsed: "시간 경과",
  battery_below: "배터리",
  operator_choice: "운용자 선택",
  signal_received: "신호 수신",
};

export const DOMAIN_LABEL: Record<Domain, string> = { air: "드론", sea: "수상정", ground: "지상" };

function targetText(t: unknown): string {
  if (t === "nearest") return "가장 가까운 표적";
  if (t === "operator") return "운용자가 고름";
  if (typeof t === "string") return t;
  if (t && typeof t === "object" && "lat" in t && "lon" in t) {
    const p = t as { lat: number; lon: number };
    return `${p.lat.toFixed(3)}, ${p.lon.toFixed(3)}`;
  }
  return "";
}

export function describeAction(a: Action): string {
  const p = a.params ?? {};
  let head = ACTION_LABEL[a.kind];
  if (Array.isArray(p.route)) head += ` ${p.route.length}점`;
  const parts = [head];
  if (p.target !== undefined) parts.push(targetText(p.target));
  if (typeof p.distance_m === "number") parts.push(`${p.distance_m}m 거리`);
  return parts.filter(Boolean).join(" · ");
}

export function describeCondition(c: Condition): string {
  const p = c.params ?? {};
  if (c.kind === "battery_below" && p.pct !== undefined) return `배터리 ${p.pct}% 미만`;
  const rest = Object.entries(p).map(([k, v]) => `${k} ${v}`);
  return [CONDITION_LABEL[c.kind], ...rest].join(" ");
}
