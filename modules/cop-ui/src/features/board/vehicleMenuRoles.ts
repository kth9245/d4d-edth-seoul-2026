import type { ActionKind, Role, VehicleSpec } from "../../contracts.gen";

export interface MenuRole { id: string; name: string; strike: boolean }

const TARGET_KINDS: ActionKind[] = ["watch_target", "approach_target", "strike_target"];

// What the vehicle menu offers (decisions 0058, 0059): roles of the vehicle's domain whose every action it can do
// (its capabilities; an operation without an ontology has none, then this rule is skipped except for strike, which
// needs strike_target among them, decision 0058), never an enemy's role.
// A role whose first step works the target the operator gives (as runtime spot_reports reads it, plus strike) or
// patrols around where a target was seen (anchor "target", decision 0055) is a target role, pointed at a seen enemy
// or a map target; the rest switch at once and leave out the role it runs now.
export function vehicleMenuRoles(roles: Role[], spec: VehicleSpec, enemyRoleIds: string[], currentRoleId: string | null):
  { plain: MenuRole[]; target: MenuRole[] } {
  const can = spec.capabilities ?? [];
  const strikes = (r: Role) => r.steps.some((s) => s.do.kind === "strike_target");
  const usable = roles.filter((r) => !enemyRoleIds.includes(r.id) && (r.domains ?? []).includes(spec.domain)
    && (can.length === 0 ? !strikes(r) : r.steps.every((s) => can.includes(s.do.kind))));
  const first = (r: Role) => r.steps.find((s) => s.id === r.entry);
  const picks = (r: Role) => {
    const s = first(r);
    return !!s && ((TARGET_KINDS.includes(s.do.kind) && s.do.params?.target === "operator") || s.do.params?.anchor === "target");
  };
  const item = (r: Role): MenuRole => ({ id: r.id, name: r.name, strike: first(r)?.do.kind === "strike_target" });
  return {
    plain: usable.filter((r) => !picks(r) && r.id !== currentRoleId).map(item),
    target: usable.filter(picks).map(item),
  };
}
