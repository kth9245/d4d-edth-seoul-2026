import type { SwitchIn } from "../../contracts.gen";
import { postJson, type Sent } from "../cards/postJson";

// A target-less role from the vehicle menu (decision 0059): the button showed now -> new, the press is the approval,
// so one approved request the gateway applies next tick (one operator action, no pending card).
export function postRole(vehicle: string, role: string): Promise<Sent> {
  const body: SwitchIn = { role_by_vehicle: { [vehicle]: role }, approve: true };
  return postJson("/injections", body);
}
