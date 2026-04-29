import paho.mqtt.client as mqtt
import time
from simulation import simulate_data



# create publisher
client = mqtt.Client()


def connect_with_retry(host, port, keepalive, retries=20, delay=2):
    for attempt in range(1, retries + 1):
        try:
            client.connect(host, port, keepalive)
            return
        except OSError:
            print(f"MQTT not ready yet, retrying ({attempt}/{retries})...")
            time.sleep(delay)

    raise ConnectionError("Unable to connect to MQTT broker after multiple retries.")


connect_with_retry("mqtt", 1883, 60)   # service name

TOPIC = "iot/sensor"

# start loop
client.loop_start()

#loop
while True:
    try:
        payload = simulate_data()
        client.publish(TOPIC, payload)    # publish sensor data to mqtt broker
        time.sleep(2)

    except KeyboardInterrupt:
        print("Manually stopped the sensor")
        break
