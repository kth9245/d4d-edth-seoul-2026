import type { SwitchIn } from "../../contracts.gen";
import { postJson, type Sent } from "../cards/postJson";

// Point a vehicle at a target with a role (decisions 0048, 0049). The menu was the preview and the press is the
// approval, so one request the gateway records as approved (one operator action, no pending card).
export function postPoint(vehicle: string, role: string, target: string): Promise<Sent> {
  const body: SwitchIn = { role_by_vehicle: { [vehicle]: role }, target_by_vehicle: { [vehicle]: target }, approve: true };
  return postJson("/injections", body);
}
