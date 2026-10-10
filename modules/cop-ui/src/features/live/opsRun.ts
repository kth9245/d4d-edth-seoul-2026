// Whether the board on screen is 실작전 (decision 0068). LiveApp sets it; the request helpers read it.
let on = false;
export const opsRun = { get: (): boolean => on, set: (v: boolean): void => { on = v; } };
