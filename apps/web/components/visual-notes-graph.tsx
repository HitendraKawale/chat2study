"use client";

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

function buildNodes(document: VisualNotesDocument): Node[] {
  return document.nodes.map((node, index) => ({
    id: node.id,
    data: {
      label: (
        <div className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 shadow-lg">
          <div className="font-semibold">{node.label}</div>
          <div className="mt-1 text-xs uppercase tracking-wide text-slate-400">
            {node.kind}
          </div>
        </div>
      ),
    },
    position: {
      x: 80 + (index % 3) * 280,
      y: 40 + Math.floor(index / 3) * 140,
    },
    type: "default",
    draggable: false,
    selectable: false,
  }));
}

function buildEdges(document: VisualNotesDocument): Edge[] {
  return document.edges.map((edge, index) => ({
    id: `${edge.source}-${edge.target}-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label ?? undefined,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
    animated: false,
  }));
}

function InnerGraph({ document }: Props) {
  const nodes = buildNodes(document);
  const edges = buildEdges(document);

  return (
    <div className="h-[460px] w-full overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        proOptions={{ hideAttribution: true }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
      >
        <Background />
        <MiniMap />
        <Controls />
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
