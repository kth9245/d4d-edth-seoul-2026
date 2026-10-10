import { opsRun } from "../live/opsRun";
import { runPath } from "../live/runPath";

// GET /mavlink (decision 0064): this run's passed commands as MAVLink message lines.
// null on any failure, so the log panel keeps the lines it already shows.
export async function fetchMavlink(): Promise<string[] | null> {
  try {
    const res = await fetch(runPath("/mavlink", opsRun.get())); // 실작전 reads its own run (decision 0068)
    return res.ok ? ((await res.json()) as string[]) : null;
  } catch {
    return null;
  }
}
