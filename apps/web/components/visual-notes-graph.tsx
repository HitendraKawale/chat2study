"use client";

import Dagre from "@dagrejs/dagre";
import {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  type Edge,
  type Node,
} from "@xyflow/react";

import type { VisualNotesDocument } from "@/types/api";

type Props = {
  document: VisualNotesDocument;
};

const KIND_COLORS: Record<string, string> = {
  concept: "border-blue-700 bg-blue-950/60",
  topic: "border-violet-700 bg-violet-950/60",
  outcome: "border-emerald-700 bg-emerald-950/60",
  question: "border-amber-700 bg-amber-950/60",
  default: "border-slate-700 bg-slate-900",
};

function getLayoutedElements(rawNodes: Node[], rawEdges: Edge[]) {
  const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "TB", nodesep: 70, ranksep: 90, marginx: 20, marginy: 20 });

  rawEdges.forEach((e) => g.setEdge(e.source, e.target));
  rawNodes.forEach((n) => g.setNode(n.id, { width: 190, height: 64 }));
  Dagre.layout(g);

  return {
    nodes: rawNodes.map((n) => {
      const pos = g.node(n.id);
      return { ...n, position: { x: pos.x - 95, y: pos.y - 32 } };
    }),
    edges: rawEdges,
  };
}

function buildElements(document: VisualNotesDocument): { nodes: Node[]; edges: Edge[] } {
  const rawNodes: Node[] = document.nodes.map((n) => ({
    id: n.id,
    data: {
      label: (
        <div
          className={`rounded-xl border px-3 py-2 text-left shadow-md ${KIND_COLORS[n.kind] ?? KIND_COLORS.default}`}
        >
          <div className="text-sm font-semibold text-slate-100 leading-snug">{n.label}</div>
          <div className="mt-0.5 text-[10px] uppercase tracking-wide text-slate-400">{n.kind}</div>
        </div>
      ),
    },
    position: { x: 0, y: 0 },
    type: "default",
    style: { background: "transparent", border: "none", padding: 0 },
  }));

  const rawEdges: Edge[] = document.edges.map((e, i) => ({
    id: `${e.source}-${e.target}-${i}`,
    source: e.source,
    target: e.target,
    label: e.label ?? undefined,
    labelStyle: { fill: "#94a3b8", fontSize: 11 },
    labelBgStyle: { fill: "#0f172a", fillOpacity: 0.85 },
    markerEnd: { type: MarkerType.ArrowClosed, color: "#475569" },
    style: { stroke: "#475569" },
  }));

  return getLayoutedElements(rawNodes, rawEdges);
}

function InnerGraph({ document }: Props) {
  const { nodes, edges } = buildElements(document);

  return (
    <div className="h-[500px] w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable={false}
      >
        <Background color="#1e293b" gap={20} />
        <MiniMap
          nodeColor="#334155"
          maskColor="rgba(2,6,23,0.7)"
          style={{ background: "#0f172a", border: "1px solid #1e293b" }}
        />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

export function VisualNotesGraph({ document }: Props) {
  return (
    <ReactFlowProvider>
      <InnerGraph document={document} />
    </ReactFlowProvider>
  );
}
