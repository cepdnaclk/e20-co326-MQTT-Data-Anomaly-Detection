import json
import random
import time


USE_CASE = "Motor overheating monitoring with relay trip simulation"
GROUP_ID = "CO326"
EDGE_NODE_ID = "Plant1.Line1.MotorCell"
DEVICE_ID = "Motor01"

TEMP_WARN_C = 75.0
TEMP_TRIP_C = 85.0
TEMP_RESET_C = 68.0


class MotorOverheatSimulation:
    def __init__(self):
        self.temperature_c = 58.0
        self.relay_command = "AUTO"
        self.relay_feedback = "CLOSED"
        self.trip_reason = "NONE"
        self.seq = 0
        self.last_update = time.time()

    def apply_command(self, payload):
        command = _extract_command(payload)
        if command is None:
            return None

        if command == "TRIP":
            self.relay_command = "TRIP"
            self.relay_feedback = "OPEN"
            self.trip_reason = "MANUAL_TRIP"
        elif command == "RESET":
            self.relay_command = "RESET"
            if self.temperature_c <= TEMP_RESET_C:
                self.relay_feedback = "CLOSED"
                self.trip_reason = "NONE"
            else:
                self.relay_feedback = "OPEN"
                self.trip_reason = "RESET_BLOCKED_HOT"
        elif command == "AUTO":
            self.relay_command = "AUTO"
            if self.temperature_c <= TEMP_RESET_C:
                self.relay_feedback = "CLOSED"
                self.trip_reason = "NONE"

        return command

    def sample(self):
        now = time.time()
        elapsed = max(0.2, min(now - self.last_update, 5.0))
        self.last_update = now

        if self.relay_feedback == "CLOSED":
            overload = 1.0 if random.random() > 0.18 else random.uniform(1.8, 3.2)
            heating = random.uniform(0.55, 1.35) * overload * elapsed
            cooling = max(0.0, (self.temperature_c - 32.0) * 0.012 * elapsed)
            self.temperature_c += heating - cooling
        else:
            self.temperature_c -= random.uniform(1.8, 3.0) * elapsed

        self.temperature_c += random.uniform(-0.35, 0.35)
        self.temperature_c = max(30.0, min(self.temperature_c, 105.0))

        if self.relay_command in ("AUTO", "RESET"):
            if self.temperature_c >= TEMP_TRIP_C:
                self.relay_feedback = "OPEN"
                self.trip_reason = "AUTO_OVER_TEMP"
            elif self.temperature_c <= TEMP_RESET_C and self.relay_command == "AUTO":
                self.relay_feedback = "CLOSED"
                self.trip_reason = "NONE"

        self.seq += 1
        temperature = round(self.temperature_c, 2)
        over_temperature = temperature >= TEMP_WARN_C
        run_state = "RUNNING" if self.relay_feedback == "CLOSED" else "TRIPPED"
        timestamp_ms = int(now * 1000)

        payload = {
            "timestamp": timestamp_ms,
            "seq": self.seq,
            "namespace": "spBv1.0",
            "group_id": GROUP_ID,
            "edge_node_id": EDGE_NODE_ID,
            "device_id": DEVICE_ID,
            "use_case": USE_CASE,
            "metrics": [
                _metric("Motor/WindingTemperature", "Float", temperature, timestamp_ms, "degC"),
                _metric("Relay/CommandedState", "String", self.relay_command, timestamp_ms),
                _metric("Relay/FeedbackState", "String", self.relay_feedback, timestamp_ms),
                _metric("Motor/RunState", "String", run_state, timestamp_ms),
                _metric("Motor/TripReason", "String", self.trip_reason, timestamp_ms),
                _metric("Motor/OverTemperature", "Boolean", over_temperature, timestamp_ms),
            ],
            "values": {
                "motorTemperatureC": temperature,
                "relayCommand": self.relay_command,
                "relayFeedback": self.relay_feedback,
                "motorState": run_state,
                "tripReason": self.trip_reason,
                "overTemperature": over_temperature,
            },
        }

        return payload

    def birth_payload(self):
        timestamp_ms = int(time.time() * 1000)
        return {
            "timestamp": timestamp_ms,
            "namespace": "spBv1.0",
            "group_id": GROUP_ID,
            "edge_node_id": EDGE_NODE_ID,
            "device_id": DEVICE_ID,
            "use_case": USE_CASE,
            "metrics": [
                _metric("Device/UseCase", "String", USE_CASE, timestamp_ms),
                _metric("Motor/WindingTemperature", "Float", self.temperature_c, timestamp_ms, "degC"),
                _metric("Relay/Command", "String", "AUTO|TRIP|RESET", timestamp_ms),
                _metric("Relay/FeedbackState", "String", self.relay_feedback, timestamp_ms),
            ],
        }


def _metric(name, datatype, value, timestamp_ms, unit=None):
    metric = {
        "name": name,
        "datatype": datatype,
        "value": value,
        "timestamp": timestamp_ms,
    }
    if unit:
        metric["unit"] = unit
    return metric


def _extract_command(payload):
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"command": payload}

    command = payload.get("command")
    if command is None:
        for metric in payload.get("metrics", []):
            if metric.get("name") == "Relay/Command":
                command = metric.get("value")
                break

    if command is None:
        return None

    command = str(command).strip().upper()
    if command in {"TRIP", "RESET", "AUTO"}:
        return command

    return None


SIMULATION = MotorOverheatSimulation()


def simulate_data():
    payload = SIMULATION.sample()
    encoded = json.dumps(payload)
    print(encoded)
    return encoded


def handle_control_payload(payload):
    command = SIMULATION.apply_command(payload)
    if command:
        print(f"Applied relay command: {command}")
    return command


def get_birth_payload():
    return json.dumps(SIMULATION.birth_payload())


def simulate_data_for_ML_training():
   
    # initialize simulation state
    sim = MotorOverheatSimulation()
    
    # used apply command
    test_command = random.choice(["AUTO", "TRIP", "NONE"])
    if test_command != "NONE":
        sim.apply_command({"command": test_command})

    # random starting temp
    sim.temperature_c = random.uniform(35.0, 95.0)

    # using sample() for overload/heating/cooling logic
    for _ in range(random.randint(3, 8)):
        latest_payload = sim.sample()

    # extract values from same payload
    values = latest_payload["values"]
    
    # define labels
    label = 1 if values["motorState"] == "TRIPPED" else 0

    training_data = {
        "motorTemperatureC": values["motorTemperatureC"],
        "relayCommand": values["relayCommand"],
        "relayFeedback": values["relayFeedback"],
        "overTemperature": int(values["overTemperature"]),
        "label": label,
        "tripReason": values["tripReason"]
    }

    payload = json.dumps(training_data)
    print(f"Full-Logic Training Sample: {payload}")
    return payload