// The route window (Part1-41): a click on the previous point's spot (a double click is two clicks) adds nothing.
export function addUnlessSame<T>(list: T[], item: T, key: (t: T) => string): T[] {
  const last = list.at(-1);
  return last !== undefined && key(last) === key(item) ? list : [...list, item];
}
