import { Background, BackgroundVariant, Controls, type Edge, MarkerType, ReactFlow, type ReactFlowInstance, useNodesState } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useRef } from "react";
import type { Play, ValidationIssue } from "../../contracts.gen";
import { type EdgeKind, layoutSteps, stepEdges } from "./playGraph";
import { StepNode, type StepNodeType } from "./StepNode";

const nodeTypes = { step: StepNode };
const FIT = { padding: 0.15, maxZoom: 1 };
// Edge colors follow theme.css (--live, --hostile, --line2); SVG attributes cannot read CSS variables.
const STROKE: Record<EdgeKind, string> = { normal: "#8e8e93", choice: "#4ade80", issue: "#ef4444" };

type Props = {
  play: Play;
  issues: Record<string, ValidationIssue[]>;
  freshStep?: string;
  playName: (id: string) => string | null;
  onOpen: (playId: string) => void;
  onInsertReport?: (stepId: string) => void;
  selectedStep?: string | null;
  onSelectStep?: (stepId: string | null) => void;
};

// Steps on a canvas, left to right from the entry, joined by one dashed edge per exit labelled by its condition.
// The layout is computed (not saved). The canvas is rebuilt (and refit) when the play, its set of steps or its
// check result changes; edits inside a card update the nodes in place. Clicking a card selects it for editing.
export function PlayGraph({ play, issues, freshStep, playName, onOpen, onInsertReport, selectedStep, onSelectStep }: Props) {
  // React Flow fits the view only when it mounts; refit whenever the box changes size (window resize, sidebar).
  const box = useRef<HTMLDivElement>(null);
  const flow = useRef<ReactFlowInstance<StepNodeType, Edge> | null>(null);
  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(() => flow.current?.fitView(FIT));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const { nodes, edges, key } = useMemo(() => {
    const pos = layoutSteps(play);
    const nodes: StepNodeType[] = play.steps.map((step) => ({
      id: step.id, type: "step", position: pos[step.id], selected: step.id === selectedStep,
      data: { step, play, issues: issues[step.id] ?? [], fresh: step.id === freshStep, playName, onOpen,
        onInsertReport: onInsertReport && (() => onInsertReport(step.id)) },
    }));
    const edges: Edge[] = stepEdges(play, new Set(Object.keys(issues))).map((e) => ({
      // Long labels are cut on the edge (the card's 연결 row keeps the full text).
      id: e.id, source: e.source, sourceHandle: e.sourceHandle, target: e.target, type: "default",
      label: e.label.length > 13 ? `${e.label.slice(0, 13)}…` : e.label,
      className: `edge-${e.kind}`, animated: e.kind === "choice",
      style: { stroke: STROKE[e.kind], strokeWidth: 1.6, strokeDasharray: "6 5" },
      markerEnd: { type: MarkerType.ArrowClosed, color: STROKE[e.kind], width: 16, height: 16 },
      labelStyle: { fill: STROKE[e.kind], fontSize: 11, fontWeight: 600 },
      labelBgStyle: { fill: "#000000", fillOpacity: 0.85 }, labelBgPadding: [6, 3] as [number, number],
    }));
    const key = `${play.id}|${play.steps.map((s) => s.id).join(",")}|${Object.keys(issues).join(",")}|${freshStep ?? ""}`;
    return { nodes, edges, key };
  }, [play, issues, freshStep, playName, onOpen, onInsertReport, selectedStep]);
  // Controlled nodes, so a card shows its edited content; keep the measured size until it is measured again.
  const [rfNodes, setRfNodes, onNodesChange] = useNodesState<StepNodeType>(nodes);
  useEffect(() => {
    setRfNodes((prev) => nodes.map((n) => ({ ...n, measured: prev.find((p) => p.id === n.id)?.measured })));
  }, [nodes, setRfNodes]);

  return (
    <div className="workflow-graph" ref={box}>
      <ReactFlow key={key} nodes={rfNodes} edges={edges} onNodesChange={onNodesChange} nodeTypes={nodeTypes} colorMode="dark"
        onNodeClick={(_, n) => onSelectStep?.(n.id)} onPaneClick={() => onSelectStep?.(null)}
        fitView fitViewOptions={FIT} minZoom={0.3} nodesConnectable={false} onInit={(i) => (flow.current = i)}
        edgesFocusable={false} proOptions={{ hideAttribution: true }}>
        <Background variant={BackgroundVariant.Lines} gap={32} color="#ffffff0a" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
