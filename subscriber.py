
# Import library
import paho.mqtt.client as mqtt
import ssl
import time
import json
import numpy as np
import joblib
import numpy as np
import json

# loaqd ml model
bundle = joblib.load("full_model.pkl")

xgb_model = bundle["xgb_model"]
iso_model = bundle["iso_model"]
threshold = bundle["threshold"]
strategy = bundle["strategy"]


####   client >>> only subscribe and receive data


# data receive at this
SUB_TOPIC = "co326/sensor/data"

# connect and subscribe to topic
def on_connect(client, userdata, flags, rc, properties=None):
    print("Subscriber Connected with the result code",rc)
    client.subscribe(SUB_TOPIC)       # subscribe

# receive msg and print if anomaly
def on_message(client, userdata, msg):

    data = json.loads(msg.payload.decode())

    temp = data["temperature"]
    humidity = data["humidity"]

    X = np.array([[temp, humidity]])

    #rule based model
    temp_anomaly = not (19 <= temp <= 36)
    humidity_anomaly = not (29 <= humidity <= 71)

    rule_pred = 1 if (temp_anomaly or humidity_anomaly) else 0

  
    # hybrid ml mdel
    xgb_prob = xgb_model.predict_proba(X)[:, 1][0]
    xgb_pred = 1 if xgb_prob > threshold else 0

    iso_pred = iso_model.predict(X)[0]
    iso_pred = 1 if iso_pred == -1 else 0

    if strategy == "and":
        ml_pred = 1 if (xgb_pred == 1 and iso_pred == 1) else 0
    else:
        ml_pred = 1 if (xgb_pred == 1 or iso_pred == 1) else 0

    #comparison
    print("\n-----------------------------")
    print(f"Temp: {temp}, Humidity: {humidity}")

    print(f"Rule-based prediction : {rule_pred}")
    print(f"ML-based prediction   : {ml_pred}")

    # highlight differences
    if rule_pred != ml_pred:
        print("⚠️ DISAGREEMENT between models!")
    elif ml_pred == 1:
        print("⚠️ BOTH agree: ANOMALY")
    else:
        print("🟢 BOTH agree: NORMAL")
"""
def on_message(client, userdata, msg):
    #print("Received ", msg.payload.decode())

    data = json.loads(msg.payload.decode())

    temp = data["temperature"]
    humidity = data["humidity"]

    # check anomalies
    temp_anomaly = not (19 <= temp <= 36)
    humidity_anomaly = not (29 <= humidity <= 71)

    if temp_anomaly:
        print("⚠️ Temperature anomaly:", temp)

    if humidity_anomaly:
        print("⚠️ Humidity anomaly:", humidity)

    if not temp_anomaly and not humidity_anomaly:
        print(f"🟢 Normal data: \n Temp: {temp}\n Humidity:{humidity}\n \n")

"""
def on_disconnect(client, userdata, rc, properties=None):
    print("Disconnected: ",rc)
    client.unsubscribe(SUB_TOPIC)

# err situation
def on_err(client, userdata, err):
    print("Got Error: ",err)

# create  client with mqtt5
subscriber = mqtt.Client(client_id="co326_subscriber_client", protocol=mqtt.MQTTv5)


# calll functions
subscriber.on_connect = on_connect
subscriber.on_message = on_message

subscriber.on_disconnect = on_disconnect

# define connect
subscriber.connect("broker.hivemq.com",1883, 60)

# start loop
subscriber.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    subscriber.loop_stop()
    subscriber.disconnect()



