import random
import time
import json

def simulate_data():
    # sample iot data
    temperature = random.uniform(20.0, 35.0)
    humidity = random.uniform(30.0, 70.0)

    # add slight variations
    temperature = random.uniform(temperature - 0.5, temperature + 0.5)
    humidity = random.uniform(humidity - 0.5, humidity + 0.5)

    # add anomaly
    if(random.random()< 0.1):
        temperature += random.uniform(10, 20)
    
    if(random.random()< 0.1):
        humidity += random.uniform(10, 20)

    # round to 2 decimal places
    temperature = round(temperature, 2)
    humidity = round(humidity, 2)

    # create a dictionary
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time()
    }

    # convert to json
    payload = json.dumps(data)

    # print the data
    print(payload)

    return payload




def simulate_data_for_ML_training():
    # sample iot data
    temperature = random.uniform(20.0, 35.0)
    humidity = random.uniform(30.0, 70.0)

    label = 0   # 0 = normal, 1 = anomaly

    # add slight variations
    temperature = random.uniform(temperature - 0.5, temperature + 0.5)
    humidity = random.uniform(humidity - 0.5, humidity + 0.5)

    # decide if anomaly happens
    is_anomaly = random.random() < 0.3
    
    if is_anomaly:
        label =1 
        # choose anomaly type
        if random.random() < 0.5:
            temperature += random.uniform(10, 20)
        else:
            humidity += random.uniform(10, 20)

    # round to 2 decimal places
    temperature = round(temperature, 2)
    humidity = round(humidity, 2)

    # create a dictionary
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time(),
        "label": label
    }

    # convert to json
    payload = json.dumps(data)

    # print the data
    print(payload)

    return payload
