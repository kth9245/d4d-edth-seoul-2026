import { describe, expect, it } from "vitest";
import { playRequest, speedPress } from "./speedPress";

describe("speed buttons (QA finding 3)", () => {
  it("while running, a speed button changes the speed right away", () => {
    expect(speedPress(true, 30)).toEqual({ request: "/run/live?speed=30" });
  });
  it("while paused, a speed button only remembers the speed; nothing starts", () => {
    expect(speedPress(false, 30)).toEqual({ remember: 30 });
  });
  it("play starts at the remembered speed, else at the run's own; pause sends 0", () => {
    expect(playRequest(false, 1, 30)).toBe("/run/live?speed=30");
    expect(playRequest(false, 5, null)).toBe("/run/live?speed=5");
    expect(playRequest(true, 5, 30)).toBe("/run/live?speed=0");
  });
});
