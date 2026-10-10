import { describe, expect, it } from "vitest";
import { kstTime } from "./kstTime";

describe("kstTime", () => {
  it("shows UTC epoch ms as KST HH:MM:SS whatever the machine time zone", () => {
    expect(kstTime(1791634270000)).toBe("21:11:10");
    expect(kstTime(1791635490000)).toBe("21:31:30");
  });
  it("wraps past midnight KST", () => {
    expect(kstTime(Date.UTC(2026, 9, 10, 15, 0, 5))).toBe("00:00:05");
  });
});
