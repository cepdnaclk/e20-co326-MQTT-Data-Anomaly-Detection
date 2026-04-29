import { useCallback, useEffect, useState } from "react";
import { io } from "socket.io-client";

import "./App.css";

import AnomalyFeed from "./components/AnomalyFeed";
import Gauge from "./components/Gauge";
import LineChart from "./components/LineChart";
import StatCard from "./components/StatCard";

const socket = io("http://localhost:5000");

const MAX_POINTS = 60;
const TEMP_WARN = 75;
const TEMP_TRIP = 85;

const fmt = (v, d = 1) => (v == null || Number.isNaN(Number(v)) ? "--" : Number(v).toFixed(d));
const now = () => new Date().toLocaleTimeString("en-US", { hour12: false });

const initialLatest = {
  motorTemperatureC: null,
  relayCommand: "AUTO",
  relayFeedback: "UNKNOWN",
  motorState: "WAITING",
  tripReason: "NONE",
  rul: null,
};

export default function App() {
  const [temperatureHistory, setTemperatureHistory] = useState([]);
  const [rulHistory, setRulHistory] = useState([]);
  const [latest, setLatest] = useState(initialLatest);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState("connecting");
  const [count, setCount] = useState(0);
  const [pendingCommand, setPendingCommand] = useState(null);

  const ingest = useCallback((msg) => {
    const temperature = Number(msg.motorTemperatureC);
    if (!Number.isFinite(temperature)) return;

    const rulHours = Number(msg.rul?.rulHours);
    setTemperatureHistory((prev) => [...prev.slice(-(MAX_POINTS - 1)), temperature]);
    if (Number.isFinite(rulHours)) {
      setRulHistory((prev) => [...prev.slice(-(MAX_POINTS - 1)), rulHours]);
    }

    setLatest(msg);
    setCount((current) => current + 1);

    const relayOpen = msg.relayFeedback === "OPEN";
    const tripReason = msg.tripReason && msg.tripReason !== "NONE" ? msg.tripReason : null;
    const isCritical = relayOpen || temperature >= TEMP_TRIP;
    const shouldLog = msg.anomaly || msg.overTemperature || relayOpen || tripReason;

    if (shouldLog) {
      const entry = {
        level: isCritical ? "critical" : "warning",
        sensor: "Motor-01 Protection",
        msg: `${fmt(temperature)} C, relay ${msg.relayFeedback}, RUL ${fmt(msg.rul?.rulHours)} h${tripReason ? `, ${tripReason}` : ""}`,
        time: now(),
      };
      setEvents((prev) => [entry, ...prev].slice(0, 50));
    }
  }, []);

  useEffect(() => {
    socket.on("connect", () => setStatus("live"));
    socket.on("disconnect", () => setStatus("disconnected"));
    socket.on("motor-data", ingest);
    socket.on("relay-command-issued", ({ command }) => {
      setPendingCommand(command);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("motor-data");
      socket.off("relay-command-issued");
    };
  }, [ingest]);

  const sendRelayCommand = async (command) => {
    setPendingCommand(command);
    try {
      const response = await fetch("http://localhost:5000/api/relay-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });

      if (!response.ok) {
        throw new Error(`Command rejected with ${response.status}`);
      }
    } catch (error) {
      setEvents((prev) => [
        {
          level: "critical",
          sensor: "Dashboard Control",
          msg: error.message,
          time: now(),
        },
        ...prev,
      ].slice(0, 50));
    }
  };

  const tempDelta =
    temperatureHistory.length >= 2
      ? +(
          temperatureHistory[temperatureHistory.length - 1] -
          temperatureHistory[temperatureHistory.length - 2]
        ).toFixed(2)
      : null;
  const rulDelta =
    rulHistory.length >= 2
      ? +(rulHistory[rulHistory.length - 1] - rulHistory[rulHistory.length - 2]).toFixed(2)
      : null;
  const statusColor = {
    live: "#22c55e",
    connecting: "#f59e0b",
    disconnected: "#ef4444",
  }[status];
  const tempColor =
    latest.motorTemperatureC >= TEMP_TRIP
      ? "#ef4444"
      : latest.motorTemperatureC >= TEMP_WARN
        ? "#f59e0b"
        : "#22c55e";
  const relayOpen = latest.relayFeedback === "OPEN";

  return (
    <div className="dashboard-container">
      <header className="header">
        <div className="brand-lockup">
          <div className="brand-mark">M1</div>
          <div>
            <div className="brand-title">Motor-01 Protection Twin</div>
            <div className="stat-label">OVERHEATING MONITORING + RELAY TRIP SIMULATION</div>
          </div>
        </div>

        <div className="header-status">
          <div className="mono-text">{count.toLocaleString()} packets</div>
          <div className="mono-text" style={{ color: statusColor }}>
            <span className="live-dot" /> {status.toUpperCase()}
          </div>
        </div>
      </header>

      <main className="main-content">
        <section className="grid-stats">
          <StatCard
            label="Winding Temperature"
            value={latest.motorTemperatureC}
            unit="C"
            delta={tempDelta}
            color={tempColor}
            history={temperatureHistory}
            min={30}
            max={105}
          />
          <StatCard
            label="Estimated RUL"
            value={latest.rul?.rulHours}
            unit="h"
            delta={rulDelta}
            color={latest.rul?.status === "critical" ? "#ef4444" : "#38bdf8"}
            history={rulHistory}
            min={0}
            max={1200}
          />
          <div className="panel relay-panel">
            <div className="stat-label">Relay Physical Feedback</div>
            <div className={`relay-state ${relayOpen ? "relay-open" : "relay-closed"}`}>
              {latest.relayFeedback}
            </div>
            <div className="relay-meta">
              <span>Command {latest.relayCommand}</span>
              <span>State {latest.motorState}</span>
            </div>
            <div className="mono-text relay-reason">{latest.tripReason || "NONE"}</div>
          </div>
        </section>

        <section className="control-strip">
          <div>
            <div className="stat-label">Actuator Command</div>
            <div className="control-title">Trip relay control path</div>
          </div>
          <div className="command-buttons">
            {["AUTO", "TRIP", "RESET"].map((command) => (
              <button
                key={command}
                className={`command-button ${pendingCommand === command ? "active" : ""}`}
                type="button"
                onClick={() => sendRelayCommand(command)}
              >
                {command}
              </button>
            ))}
          </div>
        </section>

        <section className="grid-main">
          <div className="panel">
            <div className="panel-title-row">
              <div className="panel-title">Live Protection Trend</div>
              <div className="mono-text trend-legend">
                <span style={{ color: "#22c55e" }}>Temp</span>
                <span style={{ color: "#38bdf8" }}>RUL</span>
              </div>
            </div>
            <LineChart temperatureHistory={temperatureHistory} rulHistory={rulHistory} />
          </div>

          <div className="panel feed-panel">
            <div className="panel-title">Protection Events</div>
            <AnomalyFeed anomalies={events} />
          </div>
        </section>

        <section className="grid-gauges">
          <div className="panel gauge-panel">
            <div className="stat-label">Temperature Gauge</div>
            <Gauge value={latest.motorTemperatureC ?? 0} min={30} max={105} color={tempColor} unit="C" />
          </div>
          <div className="panel gauge-panel">
            <div className="stat-label">Remaining Life</div>
            <Gauge
              value={latest.rul?.remainingLifePercent ?? 0}
              min={0}
              max={100}
              color="#38bdf8"
              unit="%"
            />
          </div>
          <div className="panel">
            <div className="stat-label threshold-heading">Protection Limits</div>
            {[
              { label: "Warning", val: `>= ${TEMP_WARN} C`, color: "#f59e0b" },
              { label: "Trip", val: `>= ${TEMP_TRIP} C`, color: "#ef4444" },
              {
                label: "Stress index",
                val: fmt(latest.rul?.thermalStressIndex, 2),
                color: "#38bdf8",
              },
            ].map((item) => (
              <div key={item.label} className="threshold-row">
                <span>{item.label}</span>
                <span className="mono-text" style={{ color: item.color }}>
                  {item.val}
                </span>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
