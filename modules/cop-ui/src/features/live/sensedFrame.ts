import type { Frame } from "../../contracts.gen";
import { trackState } from "../board/trackState";

// 실작전 tab (decision 0067): the operator's screen shows only what our side knows, so an enemy no sensor has ever
// detected (track "never", the simulator's truth) leaves the Frame before anything draws it. Seen, RF-only, lost
// and struck targets stay.
export function sensedFrame(f: Frame): Frame {
  return { ...f, targets: f.targets.filter((t) => trackState(t, f.t_ms, null).k !== "never") };
}
