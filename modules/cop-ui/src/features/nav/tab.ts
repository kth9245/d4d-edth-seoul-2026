export type Tab = "editor" | "live" | "mavlink";

export function tabFromHash(hash: string): Tab {
  if (hash === "#mavlink") return "mavlink"; // decision 0063: the header's MAVLink button opens this in a new window
  return hash === "#editor" ? "editor" : "live";
}
