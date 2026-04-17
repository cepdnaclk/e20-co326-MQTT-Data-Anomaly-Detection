import paho.mqtt.client as mqtt
import time
from simulation import simulate_data

## this is edge device who makes the sensor 

# The topic we are publishing raw sensor data to
PUB_TOPIC = "co326/sensor/data"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected successfully to broker.")
    else:
        print(f"Failed to connect, return code {rc}")


# create client with mqtt5
client = mqtt.Client(client_id="co326_publisher_client", protocol=mqtt.MQTTv5)

# bind callbacks
client.on_connect = on_connect

# connect to broker.hivemq.com port 1883
client.connect("broker.hivemq.com", 1883, 60)

# start loop
client.loop_start()

# Data simulation loop
try:
    while True:
        payload = simulate_data()

        # Publish the simulated data
        result = client.publish(PUB_TOPIC, payload)
        
        status = result[0]   # status code  0>>success
        if status == 0:
            print(f"Published `{payload}` to topic `{PUB_TOPIC}`")
        else:
            print(f"Failed to send message to topic {PUB_TOPIC}")
            
        time.sleep(2) # Wait a bit before sending next data point
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.loop_stop()
    client.disconnect()
