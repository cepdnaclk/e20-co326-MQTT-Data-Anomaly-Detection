"""
edge_ai_processor.py
---------------------
Subscribes to sensor data, runs Edge AI anomaly detection, and
publishes alerts back to the MQTT broker.

Two detection methods are included:
  1. Threshold-based  – simple, always works (Task 6 minimum requirement)
  2. Z-Score / Statistical – lightweight ML-style detection (bonus marks)

Topics:
  Subscribe : sensors/<group-id>/temperature/data
  Publish   : alerts/<group-id>/temperature/status

Usage:
    python edge_ai_processor.py

Requirements:
    pip install paho-mqtt
"""

import json
import time
import math
import paho.mqtt.client as mqtt
from datetime import datetime
from collections import deque

# CONFIGURATION  ← must match publisher settings

BROKER_HOST  = "broker.hivemq.com"  
BROKER_PORT  = 1883
BROKER_USER  = ""
BROKER_PASS  = ""

GROUP_ID     = "group20"           
PROJECT      = "temperature"

DATA_TOPIC   = f"sensors/{GROUP_ID}/{PROJECT}/data"
ALERT_TOPIC  = f"alerts/{GROUP_ID}/{PROJECT}/status"

# EDGE AI — ANOMALY DETECTION ENGINE

class AnomalyDetector:
    """
    Combines two detection methods:
      1. Hard threshold  → immediate rule-based alert
      2. Z-Score         → statistical outlier detection using rolling window
    """

    #  Threshold rules 
    TEMP_HIGH    = 35.0   # °C — critical high
    TEMP_LOW     = 10.0   # °C — critical low
    HUMIDITY_HIGH = 85.0  # %

    # Z-Score settings 
    WINDOW_SIZE  = 20     # rolling window of past readings
    Z_THRESHOLD  = 2.5    # flag if value deviates > 2.5 standard deviations

    def __init__(self):
        self.temp_window = deque(maxlen=self.WINDOW_SIZE)
        self.reading_count = 0

    # helpers 
    def _mean(self, data):
        return sum(data) / len(data)

    def _std(self, data):
        m = self._mean(data)
        variance = sum((x - m) ** 2 for x in data) / len(data)
        return math.sqrt(variance)

    def _z_score(self, value, data):
        if len(data) < 5:          # not enough data yet
            return 0.0
        std = self._std(data)
        if std == 0:
            return 0.0
        return abs((value - self._mean(data)) / std)

    #  main analysis 

    def analyse(self, payload: dict) -> dict:
        """
        Run all detection methods on a single sensor reading.
        Returns a structured result dict.
        """
        temp     = payload.get("temperature", 0)
        humidity = payload.get("humidity", 0)
        self.reading_count += 1

        alerts   = []
        severity = "NORMAL"

        #  Method 1: Threshold-based detection
        if temp > self.TEMP_HIGH:
            alerts.append(f"HIGH TEMPERATURE: {temp}°C > {self.TEMP_HIGH}°C")
            severity = "CRITICAL"
        elif temp < self.TEMP_LOW:
            alerts.append(f"LOW TEMPERATURE: {temp}°C < {self.TEMP_LOW}°C")
            severity = "WARNING"

        if humidity > self.HUMIDITY_HIGH:
            alerts.append(f"HIGH HUMIDITY: {humidity}% > {self.HUMIDITY_HIGH}%")
            if severity == "NORMAL":
                severity = "WARNING"

        #  Method 2: Z-Score statistical detection 
        self.temp_window.append(temp)
        z = self._z_score(temp, list(self.temp_window))

        if z > self.Z_THRESHOLD:
            alerts.append(
                f"STATISTICAL ANOMALY: Z-Score={z:.2f} "
                f"(threshold={self.Z_THRESHOLD})"
            )
            if severity == "NORMAL":
                severity = "WARNING"

        #  Build result
        is_anomaly = len(alerts) > 0

        result = {
            "timestamp"      : datetime.utcnow().isoformat() + "Z",
            "group_id"       : GROUP_ID,
            "sensor_id"      : payload.get("sensor_id", "unknown"),
            "reading_number" : self.reading_count,

            # Measured values
            "temperature"    : temp,
            "humidity"       : humidity,

            # AI output
            "status"         : severity,
            "is_anomaly"     : is_anomaly,
            "alerts"         : alerts,
            "z_score"        : round(z, 3),

            # Context
            "window_mean"    : round(self._mean(list(self.temp_window)), 2)
                               if self.temp_window else temp,
            "ai_method"      : "Threshold + Z-Score Statistical Detection",
        }

        return result


# MQTT CALLBACKS

detector = AnomalyDetector()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connected ✓")
        client.subscribe(DATA_TOPIC, qos=1)
        print(f"[MQTT] Subscribed → {DATA_TOPIC}")
        print(f"[MQTT] Will publish alerts → {ALERT_TOPIC}")
        print("-" * 55)
    else:
        print(f"[MQTT] Connection failed (rc={rc})")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print("[ERROR] Could not decode message — skipping.")
        return

    #  Run Edge AI 
    result = detector.analyse(payload)

    #  Log to console 
    status_icon = "🚨" if result["is_anomaly"] else "✅"
    print(
        f"{status_icon} [{result['timestamp']}] "
        f"Temp={result['temperature']}°C  "
        f"Z={result['z_score']}  "
        f"Status={result['status']}"
    )
    if result["alerts"]:
        for alert in result["alerts"]:
            print(f"   ⚠  {alert}")

    #  Publish alert to MQTT 
    client.publish(ALERT_TOPIC, json.dumps(result), qos=1)

def on_publish(client, userdata, mid):
    pass  # silent success

# MAIN

def main():
    client = mqtt.Client(client_id=f"{GROUP_ID}-edge-ai")

    if BROKER_USER:
        client.username_pw_set(BROKER_USER, BROKER_PASS)

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish

    print(f"[EDGE AI] Connecting to {BROKER_HOST}:{BROKER_PORT} …")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    try:
        client.loop_forever()   # blocking — handles reconnects automatically
    except KeyboardInterrupt:
        print("\n[EDGE AI] Processor stopped.")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
