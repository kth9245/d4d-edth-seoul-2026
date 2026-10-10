import { useEffect, useState } from "react";
import type { Frame } from "../../contracts.gen";
import { parseFrame } from "./parseFrame";

export function useFrames(url: string): { frame: Frame | null; connected: boolean } {
  const [frame, setFrame] = useState<Frame | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let timer: number | undefined;
    let stopped = false;
    const connect = () => {
      ws = new WebSocket(url);
      ws.onopen = () => setConnected(true);
      ws.onmessage = (e) => {
        const f = parseFrame(e.data);
        if (f) setFrame(f); // 깨진 메시지·옛 LegacyFrame은 무시한다.
      };
      ws.onclose = () => {
        setConnected(false);
        if (!stopped) timer = window.setTimeout(connect, 1000);
      };
    };
    connect();
    return () => {
      stopped = true;
      window.clearTimeout(timer);
      ws?.close();
    };
  }, [url]);

  return { frame, connected };
}
