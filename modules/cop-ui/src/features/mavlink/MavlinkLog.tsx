import { useEffect, useRef, useState } from "react";
import { fetchMavlink } from "./fetchMavlink";
import "./mavlink.css";

// MAVLink log panel (decisions 0064, 0065): the header's MAVLink button opens it in the middle of the map column,
// "닫기" closes it. While open it reads GET /mavlink every second and keeps the newest line in view.
export function MavlinkPanel({ onClose }: { onClose: () => void }) {
  const [lines, setLines] = useState<string[]>([]);
  const box = useRef<HTMLPreElement>(null);
  useEffect(() => {
    const read = () => fetchMavlink().then((l) => l && setLines(l));
    read();
    const id = setInterval(read, 1000);
    return () => clearInterval(id);
  }, []);
  useEffect(() => {
    if (box.current) box.current.scrollTop = box.current.scrollHeight;
  }, [lines.length]);
  return (
    <div className="mavlink-log">
      <div className="ml-head">
        <b>MAVLink</b>
        <button onClick={onClose}>닫기</button>
      </div>
      <pre ref={box}>{lines.join("\n")}</pre>
    </div>
  );
}

export function MavlinkButton({ onClick }: { onClick: () => void }) {
  return <button className="mavlink-open" onClick={onClick}>MAVLink</button>;
}
