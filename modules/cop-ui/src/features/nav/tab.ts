export type Tab = "editor" | "live";

export function tabFromHash(hash: string): Tab {
  return hash === "#editor" ? "editor" : "live";
}
