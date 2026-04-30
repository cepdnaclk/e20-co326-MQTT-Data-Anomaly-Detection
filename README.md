# CO326-Computer-Systems-Engineering-Industrial-Networks-Project

## Group Members

- `E/20/259` Munasinghe S.L.
- `E/20/328` Rathnaweera R.V.C.
- `E/20/455` Dilshan W.M.N
- `E/20/456` Dulaj U.P.S.D.

## Project Overview

This project is an Industrial IoT and Digital Twin prototype for the CO326 course project. The use case is **Motor-01 overheating monitoring with relay trip simulation**: one simulated winding-temperature sensor feeds the stack, and one simulated protective relay actuator can be tripped, reset, or left in auto mode from the dashboard.

Telemetry uses a Sparkplug B topic namespace at the edge and is bridged by Node-RED into a Unified Namespace (UNS) topic for the backend, historian, and dashboard. The backend adds anomaly scoring and remaining useful life (RUL) estimation from the motor temperature trend.

Current main services in the project:

- `publisher`: simulated sensor data generator
- `mqtt`: message broker
- `node-red`: Sparkplug B to UNS flow orchestration and over-temperature trip interlock
- `ai-brain`: lightweight ESP32-style anomaly detection simulation
- `backend`: real-time processing, relay command API, historian writer, and RUL estimator
- `influxdb`: historian
- `grafana`: visualization platform
- `frontend`: dashboard UI

## Documentation

- Architecture document: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Main Ports

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:5000`
- AI Brain: `http://localhost:5001`
- Node-RED: `http://localhost:1880`
- InfluxDB: `http://localhost:8086`
- Grafana: `http://localhost:3000`

## Main MQTT Topics

- Sparkplug telemetry: `spBv1.0/CO326/DDATA/Plant1.Line1.MotorCell/Motor01`
- Sparkplug relay command: `spBv1.0/CO326/DCMD/Plant1.Line1.MotorCell/Motor01`
- UNS telemetry: `uns/CO326/Plant1/Line1/MotorCell/Motor01/telemetry`
