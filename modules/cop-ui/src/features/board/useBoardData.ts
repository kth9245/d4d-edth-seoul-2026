import { useEffect, useState } from "react";
import { type BoardData, fetchBoardData, NO_BOARD_DATA } from "./fetchBoardData";

const RETRY_MS = 3000;

// Reads roles, specs and watch points once the gateway answers (ready = a Frame arrived), and again every 3 s
// while they are still empty (the gateway was still starting), so role names and the landing ring come back.
export function useBoardData(ready: boolean): BoardData {
  const [data, setData] = useState<BoardData>(NO_BOARD_DATA);
  const empty = data.roles.length === 0 && data.vehicles.length === 0;
  useEffect(() => {
    if (!ready || !empty) return;
    const read = () => fetchBoardData().then((d) => (d.roles.length || d.vehicles.length) && setData(d));
    read();
    const timer = setInterval(read, RETRY_MS);
    return () => clearInterval(timer);
  }, [ready, empty]);
  return data;
}
