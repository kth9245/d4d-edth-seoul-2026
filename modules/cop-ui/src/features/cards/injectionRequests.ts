import type { SwitchIn } from "../../contracts.gen";
import { postJson, type Sent } from "./postJson";

// Ask for a play switch (contracts/API.md §4): a whole-operation switch button or chosen vehicles.
// The server answers with a pending Injection; it applies only after approval.
export function postSwitch(body: SwitchIn): Promise<Sent> {
  return postJson("/injections", body);
}

// Approve or reject a pending injection.
export function postSettle(injectionId: string, approve: boolean): Promise<Sent> {
  return postJson(`/injections/${encodeURIComponent(injectionId)}/${approve ? "approve" : "reject"}`);
}
