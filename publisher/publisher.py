import os
import time

import paho.mqtt.client as mqtt

from simulation import (
    DEVICE_ID,
    EDGE_NODE_ID,
    GROUP_ID,
    get_birth_payload,
    handle_control_payload,
    simulate_data,
)


MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
SPARKPLUG_DDATA_TOPIC = f"spBv1.0/{GROUP_ID}/DDATA/{EDGE_NODE_ID}/{DEVICE_ID}"
SPARKPLUG_DBIRTH_TOPIC = f"spBv1.0/{GROUP_ID}/DBIRTH/{EDGE_NODE_ID}/{DEVICE_ID}"
SPARKPLUG_DCMD_TOPIC = f"spBv1.0/{GROUP_ID}/DCMD/{EDGE_NODE_ID}/{DEVICE_ID}"

client = mqtt.Client(client_id="motor01-sparkplug-publisher")


def connect_with_retry(host, port, keepalive, retries=20, delay=2):
    for attempt in range(1, retries + 1):
        try:
            client.connect(host, port, keepalive)
            return
        except OSError:
            print(f"MQTT not ready yet, retrying ({attempt}/{retries})...")
            time.sleep(delay)

    raise ConnectionError("Unable to connect to MQTT broker after multiple retries.")


def on_connect(_client, _userdata, _flags, rc, *_properties):
    if rc != 0:
        print(f"MQTT connection failed with code {rc}")
        return

    print("Connected to MQTT broker")
    client.subscribe(SPARKPLUG_DCMD_TOPIC)
    client.publish(SPARKPLUG_DBIRTH_TOPIC, get_birth_payload(), retain=True)
    print(f"Publishing Sparkplug B telemetry on {SPARKPLUG_DDATA_TOPIC}")
    print(f"Listening for relay commands on {SPARKPLUG_DCMD_TOPIC}")


def on_message(_client, _userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        handle_control_payload(payload)
    except Exception as exc:
        print(f"Unable to apply relay command: {exc}")


client.on_connect = on_connect
client.on_message = on_message

connect_with_retry(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

while True:
    try:
        client.publish(SPARKPLUG_DDATA_TOPIC, simulate_data())
        time.sleep(2)
    except KeyboardInterrupt:
        print("Manually stopped Motor-01 publisher")
        break
