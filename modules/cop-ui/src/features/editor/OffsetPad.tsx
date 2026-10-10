import type { MouseEvent } from "react";
import type { RouteOffset } from "../../contracts.gen";
import { offsetPad } from "./offsetPad";

const SIZE = 360;

// The relative route drawn without a map (Part1-40): the vehicle at the centre, north up, a metre grid. Each click
// adds a point as north/east metres from the centre; the line starts at the vehicle and the dots carry the
// numbers of the table rows beside it.
export function OffsetPad({ offsets, onAdd }: { offsets: RouteOffset[]; onAdd: (o: RouteOffset) => void }) {
  const pad = offsetPad(offsets, SIZE);
  const marks: number[] = [];
  for (let m = -pad.half; m <= pad.half; m += pad.grid) marks.push(m);
  const [cx, cy] = pad.toXY({ north_m: 0, east_m: 0 });
  const pts = offsets.map(pad.toXY);
  const click = (e: MouseEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    onAdd(pad.fromXY(((e.clientX - r.left) / r.width) * SIZE, ((e.clientY - r.top) / r.height) * SIZE));
  };
  return (
    <figure className="offset-pad-wrap">
      <svg className="offset-pad" viewBox={`0 0 ${SIZE} ${SIZE}`} width={SIZE} height={SIZE} onClick={click}
        role="img" aria-label="상대 경로 그리기">
        {marks.map((m) => {
          const [x] = pad.toXY({ north_m: 0, east_m: m });
          const [, y] = pad.toXY({ north_m: m, east_m: 0 });
          return (
            <g key={m} className={m === 0 ? "pad-axis" : "pad-grid"}>
              <line x1={x} y1={0} x2={x} y2={SIZE} />
              <line x1={0} y1={y} x2={SIZE} y2={y} />
            </g>
          );
        })}
        <text x={cx + 4} y={12} className="pad-label">북</text>
        <text x={SIZE - 14} y={cy - 4} className="pad-label">동</text>
        {pts.length > 0 && <polyline className="pad-route" points={[[cx, cy], ...pts].map((p) => p.join(",")).join(" ")} />}
        {pts.map(([x, y], i) => (
          <g key={i} className="pad-point">
            <circle cx={x} cy={y} r={5} />
            <text x={x + 7} y={y - 7}>{i + 1}</text>
          </g>
        ))}
        <circle className="pad-origin" cx={cx} cy={cy} r={6} />
        <text x={cx + 8} y={cy + 16} className="pad-label">기체 위치</text>
      </svg>
      <figcaption>격자 {pad.grid} m · 가장자리까지 {pad.half} m</figcaption>
    </figure>
  );
}
