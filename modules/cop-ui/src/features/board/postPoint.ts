import type { SwitchIn } from "../../contracts.gen";
import { postJson, type Sent } from "../cards/postJson";

// Point a vehicle at a target with a play (decisions 0048, 0049). The menu was the preview and the press is the
// approval, so one request the gateway records as approved (one operator action, no pending card).
export function postPoint(vehicle: string, play: string, target: string): Promise<Sent> {
  const body: SwitchIn = { play_by_vehicle: { [vehicle]: play }, target_by_vehicle: { [vehicle]: target }, approve: true };
  return postJson("/injections", body);
}
