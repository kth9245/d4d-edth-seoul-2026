import type { Block, BlockReason, Frame, GeoPoint, Injection, Report, ReportKind, Target } from "../../contracts.gen";
import { kstTime } from "./kstTime";

export interface CardChoice { id: string; label: string; preview: string }
// Decision 0040: what sensing found about a contact card's target (score 0..1, rf = our vehicles picked up its emission).
export interface CardThreat { score: number; rf: boolean; line: string }
export interface Card {
  id: string;
  source: "report" | "injection" | "block";
  kind: ReportKind | BlockReason | "injection";
  vehicle: string | null;
  t_ms: number;
  time: string;
  text: string;
  choices: CardChoice[]; // only on open reports
  preview?: string; // injections: what approving switches, e.g. "d2→track_fast"; neutralized: the strike's basis
  alternative?: GeoPoint | null; // blocks: the point the safety check offers instead, sent by "대안 지점으로"
  done: string | null; // null = still needs the operator (or a block, which is an event)
  threat?: CardThreat; // contact cards whose target sensing has scored
}

// Shown from Frame.injections / Frame.blocks instead: those carry the ids the approve and alternative buttons need,
// and Report has no field pointing at them.
const SKIP: ReportKind[] = ["injection_pending", "command_blocked"];
const SETTLED: Record<string, string> = { approved: "승인됨", rejected: "거부됨" };

const switches = (pbv: Record<string, string> | undefined) =>
  Object.entries(pbv ?? {}).map(([v, p]) => `${v}→${p}`).join(" · ");

const CHECK_KO: Record<string, string> = { no_provenance: "출처", outside_zone: "구역", battery_insufficient: "배터리" };
const sameSet = (a: string[], b: string[]) => a.length === b.length && a.every((x) => b.includes(x));

// The result card of a strike (decision 0033, Part1-20): which operator decision sent which vehicles to strike
// and which checks their strike command passed. The Frame carries no Decision, so the choice name is the one on
// that decision's approval cards that moves exactly the striking vehicles (none matching = decision id only).
function strikeBasis(frame: Frame, r: Report): string | undefined {
  const strikers = frame.vehicles.filter((v) => v.target_id === r.target_id && v.active?.command.kind === "strike");
  const first = strikers[0]?.active;
  const dec = first?.command.provenance?.decision_id;
  if (!first || !dec) return undefined;
  const ids = strikers.map((v) => v.id);
  const choice = frame.reports.filter((c) => c.decision_id === dec).flatMap((c) => c.choices ?? [])
    .find((ch) => sameSet(Object.keys(ch.play_by_vehicle ?? {}), ids));
  const checks = first.checks.map((c) => CHECK_KO[c] ?? c).join("·");
  return `운용자 결정 ${dec}${choice ? ` '${choice.label}'` : ""} → ${ids.join("·")} 타격 · ${checks} 검사 통과`;
}

const KIND_KO: Record<string, string> = { boat: "보트", fast_boat: "고속정", person: "사람", unknown: "미상" };

// Target.threat is in 0.01 units; threat_reasons says what added to it (sensing score_target, decisions 0039/0040).
function threatOf(t: Target | undefined): CardThreat | undefined {
  const reasons = t?.threat_reasons ?? [];
  if (!t || reasons.length === 0) return undefined;
  const score = (t.threat ?? 0) / 100;
  const parts = [`관측 위험 ${score.toFixed(2)}`];
  for (const r of reasons) {
    if (r.startsWith("kind_")) {
      const k = r.slice("kind_".length);
      parts.push(k === "unknown" ? "스캔 전: 미상" : `스캔 판별: ${KIND_KO[k] ?? k}`);
    } else if (r === "inside_watch_radius") parts.push("기준점 반경 안 +0.30");
    else if (r === "rf_emission") parts.push("RF 방출 감지 +0.30");
    else if (r === "speed") parts.push(`속도 ${Math.hypot(t.vel_east_mps, t.vel_north_mps).toFixed(1)} m/s`);
  }
  return { score, rf: reasons.includes("rf_emission"), line: parts.join(" · ") };
}

function fromReport(r: Report, frame: Frame): Card {
  const done = r.resolved_ms == null ? null : `처리됨 ${kstTime(r.resolved_ms)}`;
  const choices = done ? [] : (r.choices ?? []).map((c) => ({ id: c.id, label: c.label, preview: switches(c.play_by_vehicle) }));
  const preview = r.kind === "target_neutralized" ? strikeBasis(frame, r) : undefined;
  const threat = r.kind === "target_detected" ? threatOf(frame.targets.find((t) => t.id === r.target_id)) : undefined;
  return { id: r.id, source: "report", kind: r.kind, vehicle: r.vehicle_id ?? null, t_ms: r.t_ms,
    time: kstTime(r.t_ms), text: r.text, choices, done, preview, ...(threat ? { threat } : {}) };
}

function fromInjection(i: Injection): Card {
  return { id: i.id, source: "injection", kind: "injection", vehicle: Object.keys(i.play_by_vehicle).join("·") || null,
    t_ms: i.t_ms, time: kstTime(i.t_ms), text: i.label, choices: [], preview: switches(i.play_by_vehicle),
    done: SETTLED[i.status ?? "pending"] ?? null };
}

function alternativeOf(b: Block): GeoPoint | null {
  const t = b.alternative?.params?.target as Partial<GeoPoint> | undefined;
  return typeof t?.lat === "number" && typeof t?.lon === "number" ? { lat: t.lat, lon: t.lon } : null;
}

function fromBlock(b: Block): Card {
  const alternative = alternativeOf(b);
  const text = alternative ? `${b.detail} · 대안 지점 있음` : b.detail;
  return { id: b.command_id, source: "block", kind: b.reason, vehicle: b.vehicle_id, t_ms: b.t_ms,
    time: kstTime(b.t_ms), text, choices: [], alternative, done: null };
}

const waits = (c: Card) => c.choices.length > 0 || (c.source === "injection" && !c.done);
const risk = (c: Card) => c.threat?.score ?? 0;

// Frame → the side column cards: the ones waiting for the operator first, riskiest on top (decision 0040, so a
// boat that starts emitting moves its card up), then the rest newest first.
export function frameCards(frame: Frame): Card[] {
  return [
    ...frame.reports.filter((r) => !SKIP.includes(r.kind)).map((r) => fromReport(r, frame)),
    ...frame.injections.map(fromInjection),
    ...frame.blocks.map(fromBlock),
  ].sort((a, b) => Number(waits(b)) - Number(waits(a)) || (waits(a) ? risk(b) - risk(a) : 0) || b.t_ms - a.t_ms);
}
