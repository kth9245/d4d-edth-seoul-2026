import type { Domain, Role } from "../../contracts.gen";

// "새로 만들기 → 직접 생성" (Part3-13.1): a role the operator writes, starting from one card that holds.
// A human-written role counts as approved (only AI drafts need the save-time approval, decision 0003).
export function blankRole(name: string, domain: Domain, existingIds: string[]): Role {
  const taken = new Set(existingIds);
  let id = "new_role";
  for (let n = 2; taken.has(id); n++) id = `new_role-${n}`;
  return {
    id, name: name.trim() || "새 Role", domains: [domain], entry: "start", origin: "human", approved: true, template: false,
    steps: [{ id: "start", name: "시작", do: { kind: "hold", params: {} }, on: [], report: null, ui: {} }],
  };
}
