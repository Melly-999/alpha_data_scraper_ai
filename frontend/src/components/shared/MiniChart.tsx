interface MiniChartProps {
  points: Array<{ x: number; y: number }>;
  stroke?: string;
}

export function MiniChart({ points, stroke = "var(--blue)" }: MiniChartProps) {
  if (points.length < 2) {
    return null;
  }

  const width = 300;
  const height = 90;
  const values = points.map((point) => point.y);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = max - min || 1;
  const polyline = points
    .map((point, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - ((point.y - min) / spread) * height;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg className="mini-chart" width={width} height={height}>
      <polyline points={polyline} fill="none" stroke={stroke} strokeWidth="2" />
    </svg>
  );
}

