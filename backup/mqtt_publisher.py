"""
mqtt_publisher.py
-----------------
Simulates a temperature sensor and publishes readings to an MQTT broker.
Topic: sensors/<group-id>/temperature/data

Usage:
    python mqtt_publisher.py

Requirements:
    pip install paho-mqtt
"""

import json
import time
import random
import math
import paho.mqtt.client as mqtt
from datetime import datetime

# CONFIGURATION  ← change these to match your setup
BROKER_HOST   = "broker.hivemq.com"  
BROKER_PORT   = 1883
BROKER_USER   = "group20"                  
BROKER_PASS   = "1234"                   

GROUP_ID      = "group20"            
PROJECT       = "temperature"

DATA_TOPIC    = f"sensors/{GROUP_ID}/{PROJECT}/data"
PUBLISH_EVERY = 3                     # seconds between readings

# SENSOR SIMULATION

def read_sensor() -> dict:
    """
    Simulates a temperature + humidity sensor.
    Occasionally injects anomalous spikes so the AI has something to catch.
    """
    now = time.time()

    # Base temperature follows a slow sine wave (simulates day/night cycle)
    base_temp = 25 + 5 * math.sin(now / 300)

    # 10% chance of an anomalous spike
    if random.random() < 0.10:
        temperature = round(base_temp + random.uniform(15, 25), 2)  # spike!
    else:
        temperature = round(base_temp + random.gauss(0, 0.8), 2)    # normal noise

    humidity = round(random.uniform(40, 70), 2)

    return {
        "timestamp"  : datetime.utcnow().isoformat() + "Z",
        "group_id"   : GROUP_ID,
        "sensor_id"  : "TEMP-SENSOR-01",
        "temperature": temperature,   # °C
        "humidity"   : humidity,      # %
    }

# MQTT CALLBACKS

def on_connect(client, userdata, flags, rc):
    codes = {
        0: "Connected successfully ✓",
        1: "Wrong protocol version",
        2: "Invalid client ID",
        3: "Broker unavailable",
        4: "Bad username/password",
        5: "Not authorised",
    }
    print(f"[MQTT] {codes.get(rc, f'Unknown error (rc={rc})')}")
    if rc == 0:
        print(f"[MQTT] Publishing to → {DATA_TOPIC}")

def on_publish(client, userdata, mid):
    pass  # called after each successful publish

# MAIN

def main():
    client = mqtt.Client(client_id=f"{GROUP_ID}-publisher")

    if BROKER_USER:
        client.username_pw_set(BROKER_USER, BROKER_PASS)

    client.on_connect = on_connect
    client.on_publish  = on_publish

    print(f"[MQTT] Connecting to {BROKER_HOST}:{BROKER_PORT} …")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    try:
        while True:
            payload = read_sensor()
            result  = client.publish(DATA_TOPIC, json.dumps(payload), qos=1)

            print(
                f"[{payload['timestamp']}] "
                f"Temp={payload['temperature']}°C  "
                f"Humidity={payload['humidity']}%  "
                f"→ {DATA_TOPIC}"
            )

            time.sleep(PUBLISH_EVERY)

    except KeyboardInterrupt:
        print("\n[MQTT] Publisher stopped.")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
