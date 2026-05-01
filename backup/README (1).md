# Edge AI Temperature Monitoring System
> **Edge AI + Industrial IoT Mini Project**

---

## Group Members
| Name | Student ID |
|------|-----------|
| Member 1 | E/20/328 |
| Member 2 | E/20/455 |
| Member 1 | E/20/456 |
| Member 2 | E/20/XXX |

---

## Project Description
A complete Edge AI system that simulates a temperature sensor, applies real-time anomaly detection at the edge, communicates alerts via MQTT, and visualizes results in a Node-RED dashboard.

---

## System Architecture

```
Simulated Sensor
      │
      ▼
mqtt_publisher.py          ← Publishes raw sensor readings
      │  MQTT: sensors/group01/temperature/data
      ▼
edge_ai_processor.py       ← Edge AI: Threshold + Z-Score detection
      │  MQTT: alerts/group01/temperature/status
      ▼
Node-RED Dashboard         ← Chart, Gauge, Alert panel
```

---

## How to Run

### Option A — Docker (recommended)
```bash
# 1. Clone the repo
git clone https://github.com/cepdnaclk/CO326-Computer-Systems-Engineering-Industrial-Networks-Project

# 2. Start everything
docker-compose up --build

# 3. Open Node-RED dashboard
open http://localhost:1880/ui
```

### Option B — Run Python directly
```bash
cd python
pip install -r requirements.txt

# Terminal 1 — start publisher
python mqtt_publisher.py

# Terminal 2 — start AI processor
python edge_ai_processor.py
```

---

## MQTT Topics Used

| Topic | Direction | Description |
|-------|-----------|-------------|
| `sensors/group20/temperature/data` | Publish | Raw sensor readings (JSON) |
| `alerts/group20/temperature/status` | Publish | AI anomaly results (JSON) |

### Data payload example
```json
{
  "timestamp": "2025-01-01T10:00:00Z",
  "group_id": "group01",
  "sensor_id": "TEMP-SENSOR-01",
  "temperature": 28.4,
  "humidity": 55.2
}
```

### Alert payload example
```json
{
  "timestamp": "2025-01-01T10:00:03Z",
  "status": "CRITICAL",
  "is_anomaly": true,
  "alerts": ["HIGH TEMPERATURE: 45.1°C > 35.0°C"],
  "z_score": 3.12,
  "ai_method": "Threshold + Z-Score Statistical Detection"
}
```

---

## Edge AI Methods

### 1. Threshold-Based Detection (Task 6 — required)
Simple rule engine with configurable limits:
- Temperature > 35°C → **CRITICAL**
- Temperature < 10°C → **WARNING**
- Humidity > 85% → **WARNING**

### 2. Z-Score Statistical Detection (bonus)
Maintains a rolling window of the last 20 readings. If a new value deviates more than 2.5 standard deviations from the mean, it is flagged as a statistical anomaly — even if it doesn't breach a hard threshold.

---

## Results
*(Add screenshots here after running)*

---

## Challenges
- Handling MQTT reconnections gracefully
- Tuning Z-Score threshold to avoid false positives
- Keeping Docker containers in sync

## Future Improvements
- Add a trained ML model (Isolation Forest / TensorFlow Lite)
- Store readings in InfluxDB for historical analysis
- Add email/Telegram alerts for critical events
