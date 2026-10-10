import type { Block, BlockReason, Frame, Injection, Report, ReportKind } from "../../contracts.gen";
import { kstTime } from "./kstTime";

export interface CardChoice { id: string; label: string; preview: string }
export interface Card {
  id: string;
  source: "report" | "injection" | "block";
  kind: ReportKind | BlockReason | "injection";
  vehicle: string | null;
  t_ms: number;
  time: string;
  text: string;
  choices: CardChoice[]; // only on open reports
  done: string | null; // null = still needs the operator (or a block, which is an event)
}

// Shown from Frame.injections / Frame.blocks instead: those carry the ids the approve and alternative buttons need,
// and Report has no field pointing at them.
const SKIP: ReportKind[] = ["injection_pending", "command_blocked"];
const SETTLED: Record<string, string> = { approved: "승인됨", rejected: "거부됨" };

function fromReport(r: Report): Card {
  const done = r.resolved_ms == null ? null : `처리됨 ${kstTime(r.resolved_ms)}`;
  const choices = done ? [] : (r.choices ?? []).map((c) => ({
    id: c.id, label: c.label,
    preview: Object.entries(c.play_by_vehicle ?? {}).map(([v, p]) => `${v}→${p}`).join(" · "),
  }));
  return { id: r.id, source: "report", kind: r.kind, vehicle: r.vehicle_id ?? null, t_ms: r.t_ms,
    time: kstTime(r.t_ms), text: r.text, choices, done };
}

function fromInjection(i: Injection): Card {
  return { id: i.id, source: "injection", kind: "injection", vehicle: Object.keys(i.play_by_vehicle).join("·") || null,
    t_ms: i.t_ms, time: kstTime(i.t_ms), text: i.label, choices: [], done: SETTLED[i.status ?? "pending"] ?? null };
}

function fromBlock(b: Block): Card {
  const text = b.alternative ? `${b.detail} · 대안 지점 있음` : b.detail;
  return { id: b.command_id, source: "block", kind: b.reason, vehicle: b.vehicle_id, t_ms: b.t_ms,
    time: kstTime(b.t_ms), text, choices: [], done: null };
}

// Frame → the side column cards, newest first.
export function frameCards(frame: Frame): Card[] {
  return [
    ...frame.reports.filter((r) => !SKIP.includes(r.kind)).map(fromReport),
    ...frame.injections.map(fromInjection),
    ...frame.blocks.map(fromBlock),
  ].sort((a, b) => b.t_ms - a.t_ms);
}
