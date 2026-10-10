import { Background, BackgroundVariant, type Edge, MarkerType, type Node, Position, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useState } from "react";
import type { ObjectGraph } from "../../contracts.gen";
import { opsRun } from "../live/opsRun";
import { runPath } from "../live/runPath";
import "./graph.css";
import { layoutObjectGraph, orientLinks } from "./objectGraphLayout";

const TYPE_KO = { vehicle: "기체", target: "표적", report: "보고 카드", decision: "결정", command: "명령", block: "차단" } as const;
// Marker color is an SVG attribute and cannot read CSS variables: theme.css --muted.
const EDGE = "#8e8e93";

// "연결 보기" (decision 0038): the objects linked to one target, fetched once from GET /graph when opened.
export function ObjectGraphView({ focus, onClose }: { focus: string; onClose: () => void }) {
  const [graph, setGraph] = useState<ObjectGraph | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    fetch(runPath(`/graph?focus=${encodeURIComponent(focus)}`, opsRun.get())) // 실작전: its own run (0068)
      .then(async (r) => {
        if (!r.ok) throw new Error(`/graph answered ${r.status}`);
        setGraph((await r.json()) as ObjectGraph);
      })
      .catch((e: Error) => setError(e.message));
  }, [focus]);
  const pos = graph ? layoutObjectGraph(graph) : {};
  const nodes: Node[] = (graph?.nodes ?? []).map((n) => ({
    id: n.id, position: pos[n.id], draggable: false, connectable: false,
    sourcePosition: Position.Right, targetPosition: Position.Left,
    className: `og-node og-${n.type}${n.id === focus ? " og-focus" : ""}`,
    data: { label: <><small>{TYPE_KO[n.type]}</small><div>{n.label}</div></> },
  }));
  const arrow = { type: MarkerType.ArrowClosed, color: EDGE };
  const edges: Edge[] = (graph ? orientLinks(graph) : []).map((l) => ({
    id: l.id, source: l.source, target: l.target, label: l.label, className: "og-edge",
    ...(l.reversed ? { markerStart: arrow } : { markerEnd: arrow }),
  }));
  return (
    <div className="object-graph">
      <div className="og-head">
        <b>{focus} 연결</b>
        <button onClick={onClose}>닫기</button>
      </div>
      {error ? <div className="og-note">연결을 불러오지 못했습니다 ({error})</div>
        : !graph ? <div className="og-note">불러오는 중…</div>
        : (
          <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{ padding: 0.15, maxZoom: 1 }}
            nodesDraggable={false} nodesConnectable={false} proOptions={{ hideAttribution: true }}>
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
          </ReactFlow>
        )}
    </div>
  );
}
