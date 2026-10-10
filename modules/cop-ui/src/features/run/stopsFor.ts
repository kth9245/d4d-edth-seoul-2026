import { RUN_STOPS, type RunStop } from "./runStops";

// "다음 사건" stops are scenes of the night demo (Part1-13.1); other operations have none (decision 0041).
export function stopsFor(scenarioId: string | null): RunStop[] {
  return scenarioId === "baengnyeong_night" ? RUN_STOPS : [];
}
