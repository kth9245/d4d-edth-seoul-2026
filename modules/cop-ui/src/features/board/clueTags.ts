import type { Target } from "../../contracts.gen";

// The clues our sensors picked up on a target: radio, heat or sound (decisions 0039, 0071). RF first.
export function clueTags(t: Pick<Target, "rf_detected" | "ir_detected" | "sound_detected">): string[] {
  return [t.rf_detected && "RF", t.ir_detected && "열", t.sound_detected && "소음"].filter((x): x is string => !!x);
}
