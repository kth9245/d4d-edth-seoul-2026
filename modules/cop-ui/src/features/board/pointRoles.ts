import type { Track } from "./trackState";
import type { MenuRole } from "./vehicleMenuRoles";

// Roles the map pointing menu offers for one target (decision 0058): the vehicle's target roles, strike only at a
// target our sensors see now, as in the vehicle menu's seen list. A lost, RF-only or never-seen target has no
// known position, and a strike at it would fly to the simulator's true position.
export function pointRoles(roles: MenuRole[], track: Track | undefined): MenuRole[] {
  return track?.k === "seen" ? roles : roles.filter((r) => !r.strike);
}
