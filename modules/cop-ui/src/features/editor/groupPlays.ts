import type { Domain, Play } from "../../contracts.gen";
import { DOMAIN_LABEL } from "./describe";

export type PlayGroup = { key: Domain | "common"; label: string; plays: Play[] };

const ORDER: (Domain | "common")[] = ["air", "sea", "ground", "common"];
const LABEL: Record<Domain | "common", string> = { ...DOMAIN_LABEL, common: "공통" };

export function groupPlays(plays: Play[]): PlayGroup[] {
  const keyOf = (p: Play) => (p.domains.length === 1 ? p.domains[0] : "common");
  return ORDER.map((key) => ({ key, label: LABEL[key], plays: plays.filter((p) => keyOf(p) === key) })).filter(
    (g) => g.plays.length > 0,
  );
}
