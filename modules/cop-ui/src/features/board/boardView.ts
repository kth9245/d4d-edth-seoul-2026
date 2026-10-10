import type { Frame } from "../../contracts.gen";
import { frameCards } from "../cards/frameCards";
import { type Queue, decisionQueue } from "./decisionQueue";
import type { BoardData } from "./fetchBoardData";
import { type Situation, situationCounts } from "./situationCounts";
import { type Stage, targetStage } from "./targetStage";
import { type Track, trackState } from "./trackState";
import { type VehicleRow, vehicleRows } from "./vehicleRows";

export interface BoardView {
  tracks: Record<string, Track>; stages: Record<string, Stage>; queue: Queue; situation: Situation; rows: VehicleRow[];
}

// Everything the live board draws from one Frame (Part1-32), computed once per Frame. Each vehicle's active
// command time tells the queue when a block was answered (anything commanded after it).
export function boardView(f: Frame, data: BoardData): BoardView {
  const watch = data.watch[0]?.pos ?? null;
  const tracks = Object.fromEntries(f.targets.map((t) => [t.id, trackState(t, f.t_ms, watch)]));
  const stages = Object.fromEntries(f.targets.map((t) => [t.id, targetStage(f, t, tracks[t.id])]));
  const lastCmdMs = Object.fromEntries(f.vehicles.map((v) => [v.id, v.active?.command.provenance?.issued_ms ?? 0]));
  const queue = decisionQueue(frameCards(f), f.t_ms, lastCmdMs);
  const names = Object.fromEntries(data.roles.map((p) => [p.id, p.name]));
  return { tracks, stages, queue, situation: situationCounts(Object.values(stages), queue), rows: vehicleRows(f, names, data.vehicles) };
}
