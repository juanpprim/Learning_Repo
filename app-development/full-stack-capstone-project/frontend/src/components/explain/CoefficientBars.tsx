// Linear-regression explainability: a coefficient bar chart.
// A linear model IS its coefficients, so this view is the whole story:
// bar length = how much one unit of the feature moves the predicted price.
//
// D3 is used for what it's best at (scales); React renders the SVG. That
// split keeps the component a pure data->markup function, easy to test.

import { scaleLinear } from "d3";
import type { Coefficient } from "../../api";

interface Props {
  coefficients: Coefficient[];
  width?: number;
}

const BAR_H = 22;
const LABEL_W = 190;

export default function CoefficientBars({ coefficients, width = 640 }: Props) {
  const max = Math.max(...coefficients.map((c) => Math.abs(c.coefficient)), 1);
  // Symmetric domain so positive (price up) and negative (price down)
  // coefficients are visually comparable around the zero axis.
  const x = scaleLinear()
    .domain([-max, max])
    .range([LABEL_W, width - 10]);

  return (
    <svg
      width={width}
      height={coefficients.length * BAR_H + 10}
      role="img"
      aria-label="Linear regression coefficients"
    >
      {/* zero axis */}
      <line x1={x(0)} x2={x(0)} y1={0} y2={coefficients.length * BAR_H} stroke="#999" />
      {coefficients.map((c, i) => {
        const negative = c.coefficient < 0;
        return (
          <g key={c.feature} data-testid="coef-bar" transform={`translate(0, ${i * BAR_H})`}>
            <text x={LABEL_W - 8} y={BAR_H / 2 + 4} textAnchor="end" fontSize={12}>
              {c.feature}
            </text>
            <rect
              x={negative ? x(c.coefficient) : x(0)}
              y={4}
              width={Math.abs(x(c.coefficient) - x(0))}
              height={BAR_H - 8}
              fill={negative ? "#d1495b" : "#3a7d44"}
            />
            <title>
              {c.feature}: {Math.round(c.coefficient).toLocaleString()}
            </title>
          </g>
        );
      })}
    </svg>
  );
}
