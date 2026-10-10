export type Tab = "editor" | "live" | "ops";

// #ops is 실작전 (decision 0067): the simulation screen without the run bar and without never-detected enemies.
export function tabFromHash(hash: string): Tab {
  return hash === "#editor" ? "editor" : hash === "#ops" ? "ops" : "live";
}
