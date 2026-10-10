import { useEffect, useState } from "react";
import { type BoardData, fetchBoardData, NO_BOARD_DATA } from "./fetchBoardData";

// Reads plays, specs and watch points once the gateway answers (ready = a Frame arrived), again if all came
// back empty (the gateway was still starting).
export function useBoardData(ready: boolean): BoardData {
  const [data, setData] = useState<BoardData>(NO_BOARD_DATA);
  const empty = data.plays.length === 0 && data.vehicles.length === 0;
  useEffect(() => {
    if (ready && empty) fetchBoardData().then(setData);
  }, [ready, empty]);
  return data;
}
