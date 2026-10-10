import type { Role, VehicleSpec } from "../../contracts.gen";

// The start roles the overview offers a vehicle (decision 0053): roles of its domain, not the ones enemies follow.
export function startRoleOptions(roles: Role[], vehicle: VehicleSpec, enemyRoleIds: string[]): { id: string; name: string }[] {
  return roles
    .filter((r) => !enemyRoleIds.includes(r.id) && (r.domains ?? []).includes(vehicle.domain))
    .map((r) => ({ id: r.id, name: r.name }));
}
