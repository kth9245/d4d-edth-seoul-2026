import type { Domain, Role } from "../../contracts.gen";
import { DOMAIN_LABEL } from "./describe";

type GroupKey = Domain | "common" | "enemy";
export type RoleGroup = { key: GroupKey; label: string; roles: Role[] };

const ORDER: GroupKey[] = ["air", "sea", "ground", "common", "enemy"];
const LABEL: Record<GroupKey, string> = { ...DOMAIN_LABEL, common: "공통", enemy: "적" };

// Roles an enemy follows (Part1-21) go into the last group, not their domain's (they are not friendly vehicles' roles).
export function groupRoles(roles: Role[], enemyRoleIds: string[] = []): RoleGroup[] {
  const keyOf = (p: Role): GroupKey =>
    enemyRoleIds.includes(p.id) ? "enemy" : p.domains.length === 1 ? p.domains[0] : "common";
  return ORDER.map((key) => ({ key, label: LABEL[key], roles: roles.filter((p) => keyOf(p) === key) })).filter(
    (g) => g.roles.length > 0,
  );
}
