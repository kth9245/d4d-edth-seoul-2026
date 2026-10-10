import type { CardChoice } from "../cards/frameCards";

export interface ChoiceRequest { what: string; options: { vehicle: string; choiceId: string }[] }

function what(rest: string): string {
  const take = rest.match(/^발생 지역 순찰\((.+)\)$/);
  if (take) return `${take[1]} 이어받기`;
  const join = rest.match(/^(\S+)와 함께 감시\((.+)\)$/);
  return join ? `${join[1]}와 함께 ${join[2]} 감시` : rest;
}

// A report card's choices (decision 0046): the card's planned choices first in the engine's order, then the
// requests to standby drones ("d3 → ...", moving exactly that drone) grouped by what they ask, one button each.
export function choiceGroups(choices: CardChoice[]): { planned: CardChoice[]; requests: ChoiceRequest[] } {
  const planned: CardChoice[] = [];
  const requests: ChoiceRequest[] = [];
  for (const ch of choices) {
    const m = ch.label.match(/^(\S+) → (.+)$/);
    if (!m || !new RegExp(`^${m[1]}→\\S+$`).test(ch.preview)) {
      planned.push(ch);
      continue;
    }
    const w = what(m[2]);
    let g = requests.find((r) => r.what === w);
    if (!g) requests.push((g = { what: w, options: [] }));
    g.options.push({ vehicle: m[1], choiceId: ch.id });
  }
  return { planned, requests };
}
