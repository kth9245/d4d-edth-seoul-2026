// 실작전 (decision 0068): requests and the WS of the 실작전 screen go to its own run, forked when its WS connects.
export function runPath(path: string, ops: boolean): string {
  return ops ? `${path}${path.includes("?") ? "&" : "?"}run=ops` : path;
}
