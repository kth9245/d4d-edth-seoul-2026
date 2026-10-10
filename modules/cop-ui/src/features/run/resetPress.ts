// "처음으로" asks for a second press instead of window.confirm: the in-app browser cancels dialogs
// at once (confirm() returns false in 1 ms), so the reset request was never sent.
export const RESET_WINDOW_MS = 3000;

export function resetPress(armedAt: number | null, now: number): "arm" | "fire" {
  return armedAt !== null && now - armedAt <= RESET_WINDOW_MS ? "fire" : "arm";
}
