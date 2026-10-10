import { useEffect, useRef, useState } from "react";
import { fetchMavlink } from "./fetchMavlink";
import "./mavlink.css";

// MAVLink log window (decision 0063): the header's MAVLink button opens #mavlink in a new window. It reads
// GET /mavlink every second and keeps the newest line in view.
export function MavlinkLog() {
  const [lines, setLines] = useState<string[]>([]);
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const read = () => fetchMavlink().then((l) => l && setLines(l));
    read();
    const id = setInterval(read, 1000);
    return () => clearInterval(id);
  }, []);
  useEffect(() => end.current?.scrollIntoView({ block: "end" }), [lines.length]);
  return (
    <div className="mavlink-log">
      <h1>MAVLink</h1>
      <pre>{lines.join("\n")}</pre>
      <div ref={end} />
    </div>
  );
}

// Header button: one named window, so a second press brings the same window back.
export function MavlinkButton() {
  return (
    <button className="mavlink-open" onClick={() => window.open("#mavlink", "rolecall-mavlink", "width=820,height=760")}>
      MAVLink
    </button>
  );
}
