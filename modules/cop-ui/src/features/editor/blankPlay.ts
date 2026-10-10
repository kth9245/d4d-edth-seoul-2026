import type { Domain, Play } from "../../contracts.gen";

// "새로 만들기 → 직접 생성" (Part3-13.1): a play the operator writes, starting from one card that holds.
// A human-written play counts as approved (only AI drafts need the save-time approval, decision 0003).
export function blankPlay(name: string, domain: Domain, existingIds: string[]): Play {
  const taken = new Set(existingIds);
  let id = "new_play";
  for (let n = 2; taken.has(id); n++) id = `new_play-${n}`;
  return {
    id, name: name.trim() || "새 플레이", domains: [domain], entry: "start", origin: "human", approved: true, template: false,
    steps: [{ id: "start", name: "시작", do: { kind: "hold", params: {} }, on: [], report: null, ui: {} }],
  };
}
