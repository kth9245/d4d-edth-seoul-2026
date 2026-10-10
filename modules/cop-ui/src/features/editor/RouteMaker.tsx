import { useState } from "react";
import type { GeoPoint, Polygon, RouteDef } from "../../contracts.gen";
import { RouteMap } from "../map/RouteMap";
import { newRoute } from "./newRoute";

type Props = {
  zone: Polygon;
  existingIds: string[];
  onSave: (route: RouteDef) => Promise<void>; // adds it on the server and puts it on the card
  onCancel: () => void;
};
type Row = { north: string; east: string }; // typed text, read as metres on save

// "＋ 경로 추가" window (decision 0054): a name, then a fixed route clicked on the map or a relative route
// typed as north/east metres per point from where the vehicle is as the card starts.
export function RouteMaker({ zone, existingIds, onSave, onCancel }: Props) {
  const [name, setName] = useState("");
  const [kind, setKind] = useState<"fixed" | "relative">("fixed");
  const [points, setPoints] = useState<GeoPoint[]>([]);
  const [rows, setRows] = useState<Row[]>([{ north: "200", east: "0" }]);
  const [error, setError] = useState<string | null>(null);
  const count = kind === "fixed" ? points.length : rows.length;
  const setRow = (i: number, next: Partial<Row>) => setRows(rows.map((r, j) => (j === i ? { ...r, ...next } : r)));
  const save = () => {
    setError(null);
    const offsets = rows.map((r) => ({ north_m: Number(r.north) || 0, east_m: Number(r.east) || 0 }));
    onSave(newRoute(name, kind, points, offsets, existingIds)).catch((e) => setError(`경로를 저장하지 못했습니다 (${String(e)})`));
  };
  return (
    <div className="route-maker-back">
      <div className="route-maker" role="dialog" aria-label="경로 추가">
        <div className="rm-head">
          <h3>경로 추가</h3>
          <button className="rm-close" aria-label="닫기" onClick={onCancel}>×</button>
        </div>
        <div className="rm-row">
          <input aria-label="경로 이름" placeholder="경로 이름" value={name} onChange={(e) => setName(e.target.value)} />
          <label><input type="radio" name="rm-kind" aria-label="고정 경로" checked={kind === "fixed"} onChange={() => setKind("fixed")} /> 고정 경로</label>
          <label><input type="radio" name="rm-kind" aria-label="상대 경로" checked={kind === "relative"} onChange={() => setKind("relative")} /> 상대 경로 (기체 위치 기준)</label>
        </div>
        {kind === "fixed" ? (
          <>
            <p className="rm-hint">지도를 누른 순서대로 점이 이어집니다. 큰 점이 시작입니다.</p>
            <RouteMap zone={zone} points={points} onAdd={(p) => setPoints((ps) => [...ps, p])} />
            <div className="rm-row">
              <span className="rm-count">점 {points.length}개</span>
              <button disabled={!points.length} onClick={() => setPoints((ps) => ps.slice(0, -1))}>마지막 점 지우기</button>
              <button disabled={!points.length} onClick={() => setPoints([])}>모두 지우기</button>
            </div>
          </>
        ) : (
          <>
            <p className="rm-hint">카드에 들어선 기체 위치에서 각 점까지의 거리(m)입니다. 남쪽·서쪽은 음수로 적습니다.</p>
            <table className="rm-offsets">
              <thead><tr><th>점</th><th>북쪽 m</th><th>동쪽 m</th><th /></tr></thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    <td><input type="number" aria-label={`점 ${i + 1} 북쪽 m`} value={r.north} onChange={(e) => setRow(i, { north: e.target.value })} /></td>
                    <td><input type="number" aria-label={`점 ${i + 1} 동쪽 m`} value={r.east} onChange={(e) => setRow(i, { east: e.target.value })} /></td>
                    <td><button aria-label={`점 ${i + 1} 지우기`} disabled={rows.length === 1} onClick={() => setRows(rows.filter((_, j) => j !== i))}>×</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button className="rm-add" onClick={() => setRows([...rows, { north: "0", east: "0" }])}>+ 점 추가</button>
          </>
        )}
        <div className="rm-foot">
          {error && <span className="save-bad">{error}</span>}
          <button onClick={onCancel}>취소</button>
          <button className="save" disabled={count === 0} onClick={save}>저장하고 이 카드에 쓰기</button>
        </div>
      </div>
    </div>
  );
}
