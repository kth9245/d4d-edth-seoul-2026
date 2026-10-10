import type { Card } from "../cards/frameCards";

export interface QueueItem { key: string; cards: Card[] }
export interface Queue { action: QueueItem[]; alerts: Card[]; history: Card[] }

const ALERT_MS = 120_000;
const ALERT_KINDS: Card["kind"][] = ["target_neutralized", "vehicle_gap", "vehicle_lost", "battery_low"];

function rank(item: QueueItem): number {
  const c = item.cards[0];
  if (c.source === "report" && c.text.startsWith("타격 승인 요청")) return 3;
  if (c.source === "block") return 2;
  if (c.source === "injection") return 1.5;
  if (c.kind === "target_select") return 0.55; // picks a switch opened: between watched and threatening boats
  return c.threat?.score ?? 0;
}

// Side column (Part1-32): what waits for the operator now, most pressing first (strike approval, block with an
// alternative, switch, then risk), with the target picks one switch opened merged into one item; fresh events
// (strike result, gap, battery, block) for 2 minutes; everything else newest first. A block asks until its
// vehicle gets a command issued after it (lastCmdMs: vehicle -> issued_ms of its active command), at most 2 min,
// so the alternative button does not vanish at ×10 before the operator presses it.
export function decisionQueue(cards: Card[], tMs: number, lastCmdMs: Record<string, number> = {}): Queue {
  const waits = (c: Card) =>
    c.source === "block"
      ? !!c.alternative && tMs - c.t_ms < ALERT_MS && (lastCmdMs[c.vehicle ?? ""] ?? 0) <= c.t_ms
      : !c.done && (c.choices.length > 0 || c.source === "injection");
  const open = cards.filter(waits);
  const picks = open.filter((c) => c.kind === "target_select");
  const merge = picks.length > 1;
  const action: QueueItem[] = open.filter((c) => !(merge && picks.includes(c))).map((c) => ({ key: c.id, cards: [c] }));
  if (merge) action.push({ key: picks.map((c) => c.id).join("+"), cards: picks });
  const newest = (a: Card, b: Card) => b.t_ms - a.t_ms;
  action.sort((a, b) => rank(b) - rank(a) || newest(a.cards[0], b.cards[0]));
  const rest = cards.filter((c) => !open.includes(c)).sort(newest);
  const fresh = (c: Card) => (ALERT_KINDS.includes(c.kind) || c.source === "block") && tMs - c.t_ms < ALERT_MS;
  return { action, alerts: rest.filter(fresh), history: rest.filter((c) => !fresh(c)) };
}
