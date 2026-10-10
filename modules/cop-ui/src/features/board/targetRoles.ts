import type { ActionKind, Domain, Role } from "../../contracts.gen";

// strike_target is never offered: a switch carries no operator decision id, so safety rule 1 would block it
// (decision 0048). Strikes go through the approval card.
const TARGET_KINDS: ActionKind[] = ["watch_target", "approach_target"];

// Roles offered when the operator points a vehicle at a target (decision 0048): their first step works a target
// and the vehicle's domain can run them.
export function targetRoles(roles: Role[], domain: Domain): Role[] {
  return roles.filter((p) => {
    const first = p.steps.find((s) => s.id === p.entry);
    return p.domains.includes(domain) && !!first && TARGET_KINDS.includes(first.do.kind);
  });
}
