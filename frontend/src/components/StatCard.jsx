import Sparkline from "./Sparkline";

const fmt = (v, d = 1) =>
  v == null || Number.isNaN(Number(v)) ? "--" : Number(v).toFixed(d);

export default function StatCard({ label, value, unit, delta, color, history, min, max }) {
  const up = delta >= 0;

  return (
    <div className="card">
      <div className="stat-label">{label}</div>
      <div className="stat-value-row">
        <span className="mono-text stat-value" style={{ color }}>
          {fmt(value)}
        </span>
        <span className="stat-unit">{unit}</span>

        {delta != null && (
          <span className="stat-delta" style={{ color: up ? "#4ade80" : "#f87171" }}>
            {up ? "UP" : "DOWN"} {fmt(Math.abs(delta))}
          </span>
        )}
      </div>
      <div className="stat-sparkline">
        <Sparkline data={history} color={color} min={min} max={max} />
      </div>
    </div>
  );
}
