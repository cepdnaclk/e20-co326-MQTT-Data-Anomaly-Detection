import { useEffect, useRef } from "react";

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

const TEMP_MIN = 30;
const TEMP_MAX = 105;
const RUL_MAX = 1200;
const TEMP_WARN = 75;
const TEMP_TRIP = 85;

export default function LineChart({ temperatureHistory, rulHistory }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    const pad = { top: 34, right: 76, bottom: 38, left: 52 };
    const innerWidth = width - pad.left - pad.right;
    const innerHeight = height - pad.top - pad.bottom;
    const count = Math.max(temperatureHistory.length, rulHistory.length);

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#0b1220";
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = "rgba(255,255,255,0.07)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i += 1) {
      const y = pad.top + (i / 4) * innerHeight;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(width - pad.right, y);
      ctx.stroke();

      const tempLabel = TEMP_MAX - ((TEMP_MAX - TEMP_MIN) / 4) * i;
      ctx.fillStyle = "#7c8798";
      ctx.font = "12px 'DM Mono', monospace";
      ctx.textAlign = "right";
      ctx.fillText(`${Math.round(tempLabel)}C`, pad.left - 10, y + 4);
    }

    const toX = (index) => pad.left + (index / Math.max(count - 1, 1)) * innerWidth;
    const tempToY = (value) => {
      const normalized = (clamp(value, TEMP_MIN, TEMP_MAX) - TEMP_MIN) / (TEMP_MAX - TEMP_MIN);
      return pad.top + innerHeight - normalized * innerHeight;
    };
    const rulToY = (value) => {
      const normalized = clamp(value, 0, RUL_MAX) / RUL_MAX;
      return pad.top + innerHeight - normalized * innerHeight;
    };

    const drawLine = (history, color, toY) => {
      if (history.length < 2) return;

      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.lineJoin = "round";
      ctx.beginPath();
      history.forEach((value, index) => {
        const x = toX(index);
        const y = toY(value);
        if (index === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
    };

    const drawThreshold = (value, color, label) => {
      const y = tempToY(value);
      ctx.setLineDash([6, 5]);
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(width - pad.right, y);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = color;
      ctx.textAlign = "left";
      ctx.font = "bold 11px 'DM Mono', monospace";
      ctx.fillText(label, width - pad.right + 8, y + 4);
    };

    drawLine(temperatureHistory, "#22c55e", tempToY);
    drawLine(rulHistory, "#38bdf8", rulToY);
    drawThreshold(TEMP_WARN, "rgba(245, 158, 11, 0.75)", "WARN");
    drawThreshold(TEMP_TRIP, "rgba(239, 68, 68, 0.85)", "TRIP");
  }, [temperatureHistory, rulHistory]);

  return (
    <div className="chart-shell">
      <canvas ref={canvasRef} width={720} height={320} />
    </div>
  );
}
