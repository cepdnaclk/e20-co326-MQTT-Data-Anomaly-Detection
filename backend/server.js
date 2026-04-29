const express = require("express");
const mqtt = require("mqtt");
const cors = require("cors");
const http = require("http");
const { Server } = require("socket.io");
const axios = require("axios");
const { InfluxDB, Point } = require("@influxdata/influxdb-client");

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
  cors: { origin: "*" },
});

const USE_CASE = "Motor overheating monitoring with relay trip simulation";
const GROUP_ID = process.env.SPARKPLUG_GROUP_ID || "CO326";
const EDGE_NODE_ID =
  process.env.SPARKPLUG_EDGE_NODE_ID || "Plant1.Line1.MotorCell";
const DEVICE_ID = process.env.SPARKPLUG_DEVICE_ID || "Motor01";
const SPARKPLUG_DCMD_TOPIC = `spBv1.0/${GROUP_ID}/DCMD/${EDGE_NODE_ID}/${DEVICE_ID}`;
const UNS_TELEMETRY_TOPIC =
  process.env.UNS_TELEMETRY_TOPIC ||
  `uns/${GROUP_ID}/Plant1/Line1/MotorCell/${DEVICE_ID}/telemetry`;
const AI_BRAIN_URL = process.env.AI_BRAIN_URL || "http://ai-brain:5001";

const TEMP_WARN_C = 75;
const TEMP_TRIP_C = 85;
const DESIGN_LIFE_HOURS = 1200;
const VALID_RELAY_COMMANDS = new Set(["AUTO", "TRIP", "RESET"]);

let latestRecord = null;
let accumulatedDamageHours = 0;
let lastRulTimestampMs = null;

const client = mqtt.connect(process.env.MQTT_URL || "mqtt://mqtt:1883", {
  clientId: "motor-dashboard-backend",
});
const influxUrl = process.env.INFLUX_URL;
const influxToken = process.env.INFLUX_TOKEN;
const influxOrg = process.env.INFLUX_ORG;
const influxBucket = process.env.INFLUX_BUCKET;

const influxWriteApi =
  influxUrl && influxToken && influxOrg && influxBucket
    ? new InfluxDB({ url: influxUrl, token: influxToken }).getWriteApi(
        influxOrg,
        influxBucket,
        "ms",
        {
          batchSize: 20,
          flushInterval: 5000,
          maxBufferLines: 1000,
          maxRetries: 2,
          minRetryDelay: 1000,
          maxRetryDelay: 5000,
        },
      )
    : null;

app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    useCase: USE_CASE,
    mqttConnected: client.connected,
    historianEnabled: Boolean(influxWriteApi),
    subscribedTopic: UNS_TELEMETRY_TOPIC,
    commandTopic: SPARKPLUG_DCMD_TOPIC,
  });
});

app.get("/api/latest", (_req, res) => {
  res.json(latestRecord || {});
});

app.get("/api/topics", (_req, res) => {
  res.json({
    telemetry: UNS_TELEMETRY_TOPIC,
    command: SPARKPLUG_DCMD_TOPIC,
    namespace: "Sparkplug B topic namespace bridged into UNS by Node-RED",
  });
});

app.post("/api/relay-command", (req, res) => {
  const command = normalizeRelayCommand(req.body?.command);

  if (!command) {
    return res.status(400).json({
      error: "command must be one of AUTO, TRIP, RESET",
    });
  }

  publishRelayCommand(command, "dashboard-api");
  res.status(202).json({
    accepted: true,
    command,
    topic: SPARKPLUG_DCMD_TOPIC,
  });
});

io.on("connection", (socket) => {
  if (latestRecord) {
    socket.emit("motor-data", latestRecord);
  }

  socket.on("relay-command", (payload, acknowledge) => {
    const command = normalizeRelayCommand(payload?.command || payload);

    if (!command) {
      acknowledge?.({ accepted: false, error: "Invalid relay command" });
      return;
    }

    publishRelayCommand(command, "dashboard-socket");
    acknowledge?.({ accepted: true, command });
  });
});

client.on("connect", () => {
  console.log("Connected to MQTT");
  client.subscribe(UNS_TELEMETRY_TOPIC, (err) => {
    if (err) {
      console.error("Unable to subscribe to UNS telemetry:", err.message);
      return;
    }
    console.log(`Subscribed to UNS telemetry: ${UNS_TELEMETRY_TOPIC}`);
  });
});

client.on("message", async (topic, message) => {
  if (topic !== UNS_TELEMETRY_TOPIC) {
    return;
  }

  try {
    const payload = JSON.parse(message.toString());
    const telemetry = normalizeTelemetry(payload, topic);

    if (!telemetry) {
      console.warn("Skipped UNS telemetry without Motor/WindingTemperature");
      return;
    }

    const modelResult = await inferMotorAnomaly(telemetry.motorTemperatureC);
    const rul = estimateRul(telemetry, modelResult.anomalyScore);

    latestRecord = {
      ...telemetry,
      anomaly: modelResult.anomaly,
      anomalyScore: modelResult.anomalyScore,
      modelProfile: modelResult.modelProfile,
      rul,
    };

    console.log(
      `Motor-01 ${telemetry.motorTemperatureC}C | relay ${telemetry.relayFeedback} | RUL ${rul.rulHours}h`,
    );

    writeToHistorian(latestRecord);
    io.emit("motor-data", latestRecord);
    io.emit("sensor-data", latestRecord);
  } catch (err) {
    console.error("Telemetry processing error:", err.message);
  }
});

function normalizeTelemetry(payload, sourceTopic) {
  const metricValues = metricsToValues(payload.metrics || []);
  const values = {
    ...metricValues,
    ...(payload.values || {}),
  };

  const motorTemperatureC = Number(
    values.motorTemperatureC ?? values["Motor/WindingTemperature"],
  );

  if (!Number.isFinite(motorTemperatureC)) {
    return null;
  }

  const timestamp = normalizeTimestamp(payload.timestamp);
  const relayFeedback = String(
    values.relayFeedback ?? values["Relay/FeedbackState"] ?? "UNKNOWN",
  ).toUpperCase();
  const relayCommand = String(
    values.relayCommand ?? values["Relay/CommandedState"] ?? "AUTO",
  ).toUpperCase();
  const tripReason = String(
    values.tripReason ?? values["Motor/TripReason"] ?? "NONE",
  ).toUpperCase();
  const motorState = String(
    values.motorState ?? values["Motor/RunState"] ?? "UNKNOWN",
  ).toUpperCase();

  return {
    timestamp,
    isoTimestamp: new Date(timestamp).toISOString(),
    sourceTopic,
    useCase: payload.useCase || payload.use_case || USE_CASE,
    namespace: payload.namespace || "UNS",
    deviceId: payload.deviceId || payload.device_id || DEVICE_ID,
    edgeNodeId: payload.edgeNodeId || payload.edge_node_id || EDGE_NODE_ID,
    motorTemperatureC: round(motorTemperatureC, 2),
    relayCommand,
    relayFeedback,
    motorState,
    tripReason,
    overTemperature:
      toBoolean(values.overTemperature ?? values["Motor/OverTemperature"]) ||
      motorTemperatureC >= TEMP_WARN_C,
  };
}

function metricsToValues(metrics) {
  return metrics.reduce((acc, metric) => {
    if (metric?.name) {
      acc[metric.name] = metric.value;
    }
    return acc;
  }, {});
}

async function inferMotorAnomaly(motorTemperatureC) {
  try {
    const response = await axios.post(`${AI_BRAIN_URL}/predict`, {
      motorTemperatureC,
    });
    return {
      anomaly: Boolean(response.data.anomaly),
      anomalyScore: Number(response.data.anomaly_score ?? 0),
      modelProfile: response.data.model_profile ?? null,
    };
  } catch (err) {
    console.error("AI Brain Error:", err.message);
    return {
      anomaly: motorTemperatureC >= TEMP_TRIP_C,
      anomalyScore: motorTemperatureC >= TEMP_TRIP_C ? 4 : 0,
      modelProfile: { name: "backend-threshold-fallback" },
    };
  }
}

function estimateRul(telemetry, anomalyScore) {
  const nowMs = telemetry.timestamp || Date.now();
  const dtHours =
    lastRulTimestampMs == null
      ? 0
      : clamp((nowMs - lastRulTimestampMs) / 3_600_000, 0, 1 / 12);
  lastRulTimestampMs = nowMs;

  const tempExcess = Math.max(0, telemetry.motorTemperatureC - 60);
  const thermalStressIndex =
    telemetry.relayFeedback === "OPEN"
      ? 0.2
      : clamp(Math.pow(2, tempExcess / 10), 0.35, 16);
  const anomalyPenalty = anomalyScore >= 2.4 ? 1.35 : 1;
  const stress = thermalStressIndex * anomalyPenalty;

  accumulatedDamageHours = clamp(
    accumulatedDamageHours + dtHours * stress,
    0,
    DESIGN_LIFE_HOURS,
  );

  const remainingLifeHours = Math.max(0, DESIGN_LIFE_HOURS - accumulatedDamageHours);
  const currentConditionRulHours =
    telemetry.relayFeedback === "OPEN"
      ? remainingLifeHours
      : remainingLifeHours / Math.max(stress, 0.1);
  const remainingLifePercent = clamp(
    (currentConditionRulHours / DESIGN_LIFE_HOURS) * 100,
    0,
    100,
  );
  const assetLifePercent = (remainingLifeHours / DESIGN_LIFE_HOURS) * 100;

  return {
    rulHours: round(currentConditionRulHours, 1),
    remainingLifePercent: round(remainingLifePercent, 1),
    assetLifePercent: round(assetLifePercent, 1),
    accumulatedDamageHours: round(accumulatedDamageHours, 4),
    thermalStressIndex: round(stress, 2),
    status: rulStatus(telemetry.motorTemperatureC, remainingLifePercent),
  };
}

function rulStatus(temperature, remainingLifePercent) {
  if (temperature >= TEMP_TRIP_C || remainingLifePercent <= 10) {
    return "critical";
  }
  if (temperature >= TEMP_WARN_C || remainingLifePercent <= 30) {
    return "warning";
  }
  return "healthy";
}

function writeToHistorian(data) {
  if (!influxWriteApi) {
    return;
  }

  const point = new Point("motor_overheat_monitor")
    .tag("device_id", data.deviceId)
    .tag("edge_node_id", data.edgeNodeId)
    .floatField("motor_temperature_c", data.motorTemperatureC)
    .floatField("anomaly_score", data.anomalyScore)
    .floatField("rul_hours", data.rul.rulHours)
    .floatField("remaining_life_percent", data.rul.remainingLifePercent)
    .floatField("asset_life_percent", data.rul.assetLifePercent)
    .floatField("thermal_stress_index", data.rul.thermalStressIndex)
    .floatField("accumulated_damage_hours", data.rul.accumulatedDamageHours)
    .booleanField("over_temperature", data.overTemperature)
    .booleanField("anomaly", Boolean(data.anomaly))
    .stringField("relay_command", data.relayCommand)
    .stringField("relay_feedback", data.relayFeedback)
    .stringField("motor_state", data.motorState)
    .stringField("trip_reason", data.tripReason)
    .timestamp(new Date(data.timestamp));

  influxWriteApi.writePoint(point);
}

function publishRelayCommand(command, requestedBy) {
  const timestamp = Date.now();
  const payload = {
    timestamp,
    namespace: "spBv1.0",
    group_id: GROUP_ID,
    edge_node_id: EDGE_NODE_ID,
    device_id: DEVICE_ID,
    command,
    requested_by: requestedBy,
    metrics: [
      {
        name: "Relay/Command",
        datatype: "String",
        value: command,
        timestamp,
      },
    ],
  };

  client.publish(SPARKPLUG_DCMD_TOPIC, JSON.stringify(payload), { qos: 0 });
  io.emit("relay-command-issued", {
    command,
    requestedBy,
    topic: SPARKPLUG_DCMD_TOPIC,
    timestamp,
  });
}

function normalizeRelayCommand(command) {
  if (command == null) {
    return null;
  }

  const normalized = String(command).trim().toUpperCase();
  return VALID_RELAY_COMMANDS.has(normalized) ? normalized : null;
}

function normalizeTimestamp(timestamp) {
  const value = Number(timestamp);

  if (!Number.isFinite(value)) {
    return Date.now();
  }

  return value < 10_000_000_000 ? value * 1000 : value;
}

function toBoolean(value) {
  if (typeof value === "boolean") {
    return value;
  }
  return String(value).toLowerCase() === "true";
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function round(value, digits = 1) {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

server.listen(5000, () => {
  console.log("Server running on port 5000");
});

process.on("SIGTERM", () => {
  influxWriteApi?.close().catch(() => {});
  process.exit(0);
});
