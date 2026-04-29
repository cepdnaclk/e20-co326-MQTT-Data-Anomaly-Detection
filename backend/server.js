const express = require("express");
const mqtt = require("mqtt");
const cors = require("cors");
const http = require("http");
const {Server} = require("socket.io");
const axios = require('axios');
const { InfluxDB, Point } = require("@influxdata/influxdb-client");

// app
const app = express();
app.use(cors());


// create a socket server for this
const server = http.createServer(app)

let rawData = {};
let latestRecord = null;

const client = mqtt.connect(process.env.MQTT_URL || "mqtt://mqtt:1883");
const influxUrl = process.env.INFLUX_URL;
const influxToken = process.env.INFLUX_TOKEN;
const influxOrg = process.env.INFLUX_ORG;
const influxBucket = process.env.INFLUX_BUCKET;

const influxWriteApi =
  influxUrl && influxToken && influxOrg && influxBucket
    ? new InfluxDB({ url: influxUrl, token: influxToken })
        .getWriteApi(influxOrg, influxBucket, "ns")
    : null;

// create websocket
const io = new Server(server,{
  cors: {origin: "*"}
});

app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    mqttConnected: client.connected,
    historianEnabled: Boolean(influxWriteApi),
  });
});

app.get("/api/latest", (_req, res) => {
  res.json(latestRecord || {});
});

function writeToHistorian(data) {
  if (!influxWriteApi) {
    return;
  }

  const point = new Point("sensor_reading")
    .floatField("temperature", Number(data.temperature))
    .floatField("humidity", Number(data.humidity))
    .booleanField("anomaly", Boolean(data.anomaly))
    .timestamp(new Date(Number(data.timestamp) * 1000 || Date.now()));

  if (typeof data.anomalyScore === "number") {
    point.floatField("anomaly_score", data.anomalyScore);
  }

  influxWriteApi.writePoint(point);
  influxWriteApi
    .flush()
    .catch((err) => console.error("InfluxDB Flush Error:", err.message));
}

// connection throgh mqtt >> backend with publisher
client.on("connect", () => {
  console.log("Connected to MQTT");
  client.subscribe("iot/sensor");
});


// add to list when msg received
client.on("message", async (topic, message) => {

  // verify topic
  if (topic== "iot/sensor"){
    try {
      rawData = JSON.parse(message.toString());

      // model to redictt anomaly
      const response = await axios.post('http://ai-brain:5001/predict',{
          temp: rawData.temperature,
          hum: rawData.humidity
      });

      const {
        anomaly,
        anomaly_score: anomalyScore = null,
        model_profile: modelProfile = null,
      } = response.data;
      latestRecord = {
        ...rawData,
        anomaly,
        anomalyScore,
        modelProfile,
      };

      console.log(`Temp: ${rawData.temperature} | Anomaly: ${anomaly} | Score: ${anomalyScore}`);
      writeToHistorian(latestRecord);

      // real time data push to frontend
      io.emit("sensor-data", latestRecord);

    } catch (err) {
      console.error("AI Brain Error:", err.message);
    }

  }
});



server.listen(5000, () => {
  console.log("Server running on port 5000");
});

process.on("SIGTERM", () => {
  influxWriteApi?.close().catch(() => {});
  process.exit(0);
});
