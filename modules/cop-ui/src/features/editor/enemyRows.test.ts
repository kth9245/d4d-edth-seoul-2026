import { describe, expect, it } from "vitest";
import scenario from "../../../../../demo/scenarios/baengnyeong_night.json";
import type { EnemySpec, Role } from "../../contracts.gen";
import { appearText, enemyRows } from "./enemyRows";

const enemies = scenario.enemies as unknown as EnemySpec[];
const roles = scenario.roles as unknown as Role[];
const started = scenario.operation.started_ms;

describe("enemyRows", () => {
  it("heads each enemy with kind, appearance, place and speed, then its role", () => {
    const [boat, fast] = enemyRows(enemies, started, roles);
    expect(boat).toMatchObject({
      id: "boat1", kind: "보트", appear: "21:11 KST 등장 (+11분)", place: "37.985, 124.700", speed: "1.0 m/s", roleId: "enemy_boat1",
    });
    expect(boat.role?.name).toBe("적: 상륙 접근");
    expect(fast).toMatchObject({ id: "fast1", kind: "고속 보트", appear: "21:23 KST 등장 (+23분)", place: "boat1 위치에서", speed: "6.3 m/s" });
  });
  it("keeps an enemy whose role is missing", () => {
    expect(enemyRows(enemies, started, [])[0]).toMatchObject({ roleId: "enemy_boat1", role: null });
  });
});

describe("appearText", () => {
  it("counts from the operation start without a start time", () => {
    expect(appearText(enemies[0], null)).toBe("+11분 등장");
  });
});
