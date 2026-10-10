import { describe, expect, it } from "vitest";
import { raidCopy, skipNote } from "./raidCopy";

describe("raidCopy", () => {
  it("asks the finder or a tracker how to deal with its enemy, all wide buttons", () => {
    const act = raidCopy("raid-e_drone-act", "d1", "e_drone");
    expect(act).toMatchObject({ question: "어떻게 대응할까요?", flat: true });
    expect(act?.hint).toContain("d1는 e_drone를 계속 따라갑니다");
    expect(raidCopy("raid-e_usv-tact-d3", "d3", "e_usv")?.flat).toBe(true);
  });

  it("picks vehicles one by one on the track, focus and cover cards", () => {
    const track = raidCopy("raid-e_usv-track-1", "d2", "e_usv");
    expect(track).toMatchObject({ question: "누구를 보낼까요?", group: "아군 고르기(한 대씩)", flat: false });
    expect(track?.hint).toContain("e_usv 추적에 붙일 아군");
    expect(raidCopy("raid-e_usv-cover-0", "d2", "e_usv")?.hint).toContain("d2가 비운 순찰");
  });

  it("asks home or hold on an idle card and leaves other cards alone", () => {
    expect(raidCopy("raid-idle-d3-1791634615000", "d3", null)).toMatchObject({ question: "어떻게 할까요?", flat: true });
    expect(raidCopy("rep-d1-1", "d1", "boat1")).toBeNull();
  });

  it("tells 대기 from 전체 대기", () => {
    expect(skipNote("track_skip")).toBe("선택 기체는 옮기지 않음");
    expect(skipNote("track_allstay")).toBe("아무 기체도 옮기지 않음");
  });
});
