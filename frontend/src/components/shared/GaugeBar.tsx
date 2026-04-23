interface GaugeBarProps {
  label: string;
  value: number;
  max: number;
}

export function GaugeBar({ label, value, max }: GaugeBarProps) {
  const percent = Math.min((value / max) * 100, 100);
  return (
    <div className="gauge">
      <div className="gauge-label">
        <span>{label}</span>
        <span>{value.toFixed(2)}</span>
      </div>
      <div className="gauge-track">
        <div className="gauge-fill" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

