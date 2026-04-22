const express = require("express");
const mqtt = require("mqtt");
const cors = require("cors");
const http = require("http")
const {Server} = require("socket.io")

// app
const app = express();
app.use(cors());


// create a socket server for this
const server = http.createServer(app)

let latestData = {};

const client = mqtt.connect(process.env.MQTT_URL || "mqtt://mqtt:1883");

// create websocket
const io = new Server(server,{
  cors: {origin: "*"}
});

// connection  >> backend with publisher
client.on("connect", () => {
  console.log("Connected to MQTT");
  client.subscribe("iot/sensor");
});


// add to list when msg received
client.on("message", (topic, message) => {

  // verify topic
  if (topic== "iot/sensor"){
    try {
      latestData = JSON.parse(message.toString());

      console.log("Received:", latestData);

      // real time data push to frontend
      io.emit("sensor-data", latestData);

    } catch (err) {
      console.log("Invalid message");
    }

  }
});


// api to return received data
app.get("/data", (req, res) => {
  res.json(latestData);
});


server.listen(5000, () => {
  console.log("Server running on port 5000");
});