import type { DirectIn, GeoPoint } from "../../contracts.gen";
import { postJson, type Sent } from "./postJson";

// Operator direct control → POST /direct (contracts/API.md §5). The safety check on the server decides
// whether it passes; a refusal comes back as a block card, not as an error here.
export function postDirect(vehicle_id: string, target: GeoPoint): Promise<Sent> {
  const body: DirectIn = { vehicle_id, target: { lat: target.lat, lon: target.lon } };
  return postJson("/direct", body);
}
