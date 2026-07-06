// LightGBM explainability: the recursive feature-space partition of one tree,
// r2d3-style. Every split ("area <= 9374?") carves the space in two; leaves
// carry the price contribution for their region. d3.hierarchy/d3.tree computes
// the layout; React renders it — same testable split as CoefficientBars.

import { hierarchy, tree as d3tree } from "d3";
import type { TreeNode } from "../../api";

interface Props {
  root: TreeNode;
  maxDepth?: number; // deep trees are unreadable; prune for display
  width?: number;
  height?: number;
}

/** Depth-limit the tree: nodes below maxDepth collapse into "…" leaves. */
function prune(node: TreeNode, depth: number, maxDepth: number): TreeNode {
  if (node.value !== undefined || depth >= maxDepth) {
    return node.value !== undefined ? node : { value: NaN }; // NaN -> rendered as "…"
  }
  return {
    ...node,
    left: node.left && prune(node.left, depth + 1, maxDepth),
    right: node.right && prune(node.right, depth + 1, maxDepth),
  };
}

const childrenOf = (n: TreeNode): TreeNode[] | undefined =>
  n.left && n.right ? [n.left, n.right] : undefined;

export default function TreePartition({ root, maxDepth = 4, width = 720, height = 360 }: Props) {
  const pruned = prune(root, 0, maxDepth);
  const h = hierarchy(pruned, childrenOf);
  // d3.tree assigns x/y so no branches overlap; margins keep labels inside.
  const layout = d3tree<TreeNode>().size([width - 40, height - 60])(h);

  return (
    <svg width={width} height={height} role="img" aria-label="LightGBM tree partition">
      <g transform="translate(20, 30)">
        {layout.links().map((link, i) => (
          <line
            key={i}
            x1={link.source.x}
            y1={link.source.y}
            x2={link.target.x}
            y2={link.target.y}
            stroke="#bbb"
          />
        ))}
        {layout.descendants().map((node, i) => {
          const d = node.data;
          const isLeaf = d.value !== undefined;
          return (
            <g key={i} data-testid="tree-node" transform={`translate(${node.x}, ${node.y})`}>
              <circle r={6} fill={isLeaf ? "#e9c46a" : "#457b9d"} />
              <text y={-10} textAnchor="middle" fontSize={11}>
                {isLeaf
                  ? Number.isNaN(d.value!)
                    ? "…"
                    : Math.round(d.value!).toLocaleString()
                  : `${d.feature} ≤ ${d.threshold}`}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}
