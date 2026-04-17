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
    if(random.random()< 0.01):
        temperature += random.uniform(10, 20)

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
