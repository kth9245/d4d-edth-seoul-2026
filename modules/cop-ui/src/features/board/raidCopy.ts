// 24h step-by-step raid cards (RT-19, RT-20; user 10/11): what each card asks, in place of the night patrol copy.
// flat: every choice is a wide button (strike/observe, home/hold); otherwise vehicles are picked one by one.
export type RaidCopy = { hint: string; question: string; group: string; flat: boolean };

const WHO: Record<string, (v: string, t: string) => string> = {
  track: (_v, t) => `${t} 추적에 붙일 아군`,
  focus: (_v, t) => `${t} 발견 지점을 집중 순찰할 아군`,
  cover: (v) => `${v}가 비운 순찰을 대신할 아군`,
};

export function raidCopy(id: string, vehicle: string | null, target: string | null): RaidCopy | null {
  if (!id.startsWith("raid-")) return null;
  const v = vehicle ?? "";
  const t = target ?? "";
  if (id.startsWith("raid-idle-")) {
    return { hint: `${v}의 임무가 끝났습니다. 기지로 돌아갈지, 지금 위치에 멈출지 고르세요.`, question: "어떻게 할까요?", group: "", flat: true };
  }
  const stage = id.slice(`raid-${t}-`.length).split("-")[0];
  if (stage === "act" || stage === "tact") {
    return { hint: `${v}는 ${t}를 계속 따라갑니다. 격추할지, 관찰을 계속할지 고르세요.`, question: "어떻게 대응할까요?", group: "", flat: true };
  }
  const who = (WHO[stage] ?? (() => "보낼 아군"))(v, t);
  return { hint: `${who}을 한 대씩 고르세요. 고를 때마다 남은 아군으로 다시 묻습니다.`, question: "누구를 보낼까요?", group: "아군 고르기(한 대씩)", flat: false };
}

// A skip button moves nobody it picked; 전체 대기 ends the questions about this enemy (user 10/11).
export const skipNote = (id: string) => (id.endsWith("_skip") ? "선택 기체는 옮기지 않음" : "아무 기체도 옮기지 않음");
