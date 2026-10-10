import type { Action, ActionKind, Condition, ConditionKind, Domain, TargetKind } from "../../contracts.gen";
import { mmss } from "../run/mmss";

export const ACTION_LABEL: Record<ActionKind, string> = {
  move_to: "경로 비행", // decision 0045: one action in the editor, 반복 tells them apart
  patrol_route: "경로 비행",
  search_area: "구역 수색",
  return_home: "귀환",
  watch_target: "표적 감시",
  watch_point: "지점 감시",
  approach_target: "표적 접근",
  relay_comms: "통신 중계",
  hold: "대기",
  strike_target: "표적 타격",
};

export const CONDITION_LABEL: Record<ConditionKind, string> = {
  target_found: "표적 발견",
  arrived: "도착",
  time_elapsed: "시간 경과",
  battery_below: "배터리",
  operator_choice: "운용자 선택",
  signal_received: "신호 수신",
  at_time: "T+ 시각",
  target_neutralized: "표적 무력화",
  target_resighted: "보고된 거점 재탐지",
};

export const DOMAIN_LABEL: Record<Domain, string> = { air: "드론", sea: "수상정", ground: "지상" };

export const TARGET_KIND_LABEL: Record<TargetKind, string> = { boat: "보트", fast_boat: "고속 보트", person: "사람", unknown: "미상", drone: "자폭 드론", usv: "적 수상정", ugv: "적 지상로봇" };

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

// Route flying (decision 0045): the route's name (or how many points), once or repeating, and whether it is relative.
function routeText(a: Action): string {
  const p = a.params ?? {};
  const name = typeof p.route_name === "string" ? p.route_name
    : Array.isArray(p.route) ? `경로 ${p.route.length}곳`
    : Array.isArray(p.offsets) ? `상대 경로 ${p.offsets.length}곳` : targetText(p.target);
  const parts = [ACTION_LABEL[a.kind], name, a.kind === "patrol_route" ? "반복" : "한 번"];
  if (Array.isArray(p.offsets)) parts.push("기체 위치 기준");
  return parts.filter(Boolean).join(" · ");
}

export function describeAction(a: Action): string {
  if (a.kind === "move_to" || a.kind === "patrol_route") return routeText(a);
  const p = a.params ?? {};
  const parts = [ACTION_LABEL[a.kind]];
  if (p.target !== undefined) parts.push(targetText(p.target));
  if (typeof p.distance_m === "number") parts.push(`${p.distance_m}m 거리`);
  return parts.filter(Boolean).join(" · ");
}

export function describeCondition(c: Condition): string {
  const p = c.params ?? {};
  if (c.kind === "battery_below" && p.pct !== undefined) return `배터리 ${p.pct}% 미만`;
  if (c.kind === "at_time") return `T+${mmss(Number(p.offset_ms ?? 0))}`;
  const rest = Object.entries(p).map(([k, v]) => `${k} ${v}`);
  return [CONDITION_LABEL[c.kind], ...rest].join(" ");
}
