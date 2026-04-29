const fmt = (v, d = 1) =>
  v == null || Number.isNaN(Number(v)) ? "--" : Number(v).toFixed(d);
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

export default function Gauge({ value, min, max, color, unit }) {
  const pct = clamp((value - min) / (max - min), 0, 1);
  const angle = -140 + pct * 280;
  const toXY = (deg, r) => {
    const rad = (deg - 90) * (Math.PI / 180);
    return [50 + r * Math.cos(rad), 50 + r * Math.sin(rad)];
  };
  const arcPath = (r, from, to) => {
    const [x1, y1] = toXY(from, r);
    const [x2, y2] = toXY(to, r);
    const large = to - from > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  };
  const [needleX, needleY] = toXY(angle, 30);

  return (
    <svg viewBox="0 0 100 70" className="gauge">
      <path
        d={arcPath(38, -140, 140)}
        fill="none"
        stroke="rgba(255,255,255,0.08)"
        strokeWidth="7"
        strokeLinecap="round"
      />
      <path
        d={arcPath(38, -140, angle)}
        fill="none"
        stroke={color}
        strokeWidth="7"
        strokeLinecap="round"
      />
      <line
        x1="50"
        y1="50"
        x2={needleX}
        y2={needleY}
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx="50" cy="50" r="3" fill={color} />
      <text x="50" y="67" textAnchor="middle" fontSize="9" fill="#9ca3af" className="mono-text">
        {fmt(value)}
        {unit}
      </text>
    </svg>
  );
}
