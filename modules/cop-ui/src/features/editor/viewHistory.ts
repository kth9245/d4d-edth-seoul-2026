// Editor navigation (뒤로 가기): which view is open (a play id or the overview) and the views opened before it.
export type ViewHistory = { current: string; stack: string[] };

export function openView(h: ViewHistory, next: string): ViewHistory {
  return next === h.current ? h : { current: next, stack: [...h.stack, h.current] };
}

// What "← 뒤로" calls a view: the fixed views (overview, ontology) by their name, a play by its name.
export function viewLabel(id: string, fixed: Record<string, string>, playName: (id: string) => string | null): string {
  return fixed[id] ?? playName(id) ?? id;
}

// Back to the view opened before this one; with nothing recorded, to `fallback` (the overview).
export function backFrom(h: ViewHistory, fallback: string): ViewHistory {
  if (h.stack.length === 0) return { current: fallback, stack: [] };
  return { current: h.stack[h.stack.length - 1], stack: h.stack.slice(0, -1) };
}
