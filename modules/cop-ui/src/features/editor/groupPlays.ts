import type { Domain, Play } from "../../contracts.gen";
import { DOMAIN_LABEL } from "./describe";

type GroupKey = Domain | "common" | "enemy";
export type PlayGroup = { key: GroupKey; label: string; plays: Play[] };

const ORDER: GroupKey[] = ["air", "sea", "ground", "common", "enemy"];
const LABEL: Record<GroupKey, string> = { ...DOMAIN_LABEL, common: "공통", enemy: "적" };

// Plays an enemy follows (Part1-21) go into the last group, not their domain's (they are not friendly vehicles' plays).
export function groupPlays(plays: Play[], enemyPlayIds: string[] = []): PlayGroup[] {
  const keyOf = (p: Play): GroupKey =>
    enemyPlayIds.includes(p.id) ? "enemy" : p.domains.length === 1 ? p.domains[0] : "common";
  return ORDER.map((key) => ({ key, label: LABEL[key], plays: plays.filter((p) => keyOf(p) === key) })).filter(
    (g) => g.plays.length > 0,
  );
}
